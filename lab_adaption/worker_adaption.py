""" """

import logging
import traceback
from typing import Optional, NamedTuple, Dict, Any, Tuple
from random import randint

from laborchestrator.database_integration import StatusDBInterface
from laborchestrator.engine import ScheduleManager
from laborchestrator.engine.worker_interface import (
    WorkerInterface,
    Observable,
    DummyHandler,
)
from laborchestrator.structures import SMProcess, MoveStep, SchedulingInstance
from sila2.client import SilaClient
from .device_wrappers import (
    DeviceInterface,
    HumanWrapper,
    GenericRobotArmWrapper,
    EchoWrapper,
)
try:
    from genericroboticarm.sila_server import Client as ArmClient
except ModuleNotFoundError:
    ArmClient = SilaClient
    logging.warning("Generic robotic arm seems to be not installed")


# Out comment those you want to simulate the steps instead of calling an actual sila server
USE_REAL_SERVERS = [
    "PFonRail",
    "Echo",
    "Human",
]
interactive = {"Echo", "Washer", "Sealer"}

# maps the device names (from the platform_config and process description) to the correct wrappers
device_wrappers: dict[str, type[DeviceInterface]] = dict(
    PFonRail=GenericRobotArmWrapper,
    Human=HumanWrapper,
    Echo=EchoWrapper,
)

# maps the device names (from the platform_config and process description) to the correct sila server names
# those without a sila server can be left out
sila_server_name: dict[str, str] = dict(
    PFonRail="PFonRail_sim",
    Echo="Echo",
    Human="Human",
)


class Worker(WorkerInterface):
    # save the clients for repeated use
    clients: dict[str, SilaClient]

    def __init__(
        self,
        jssp: SchedulingInstance,
        schedule_manager: ScheduleManager,
        db_client: StatusDBInterface,
    ):
        super().__init__(jssp, schedule_manager, db_client)
        self.clients = {}

    def execute_process_step(
        self, step_id: str, device: str, device_kwargs: Dict[str, Any]
    ) -> Observable:
        print(f"Execute {step_id} on device {device}")
        # get all information about the process step
        step = self.jssp.step_by_id[step_id]
        cont = self.jssp.container_info_by_name[step.cont_names[0]]
        if device in USE_REAL_SERVERS:
            client = self.get_client(device_name=device)
            if client:
                wrapper = device_wrappers[device]
                # starts the command on the device and returns an Observable
                observable = wrapper.get_SiLA_handler(
                    step, cont, client, **device_kwargs
                )
                return observable
        # for all simulated devices, this simply wraps a sleep command into an Observable
        # TODO you can change the time to for example step.duration/2
        handler = DummyHandler(randint(2, 12))
        # the protocol will take between 2 and 12 seconds
        handler.run_protocol(None)
        return handler

    def get_client(self, device_name, timeout: float = 5) -> SilaClient | None:
        server_name = sila_server_name.get(device_name, None)
        if server_name:
            client = self.clients.get(device_name, None)
            if client:
                # check if the server still responds
                try:
                    name = client.SiLAService.ServerName.get()
                    assert name == server_name
                except AssertionError:
                    logging.error(
                        f"The server on {client.address}:{client.port} has changed its name"
                    )
                except ConnectionError:
                    # the server seems to be offline
                    self.clients.pop(device_name)
            # try to discover the matching server by its server name
            try:
                client = SilaClient.discover(
                    server_name=server_name, insecure=True, timeout=timeout
                )
                self.clients[device_name] = client
                return client
            except TimeoutError as error:
                logging.exception(f"Could not connect to {server_name}:\n{error}")
        return None

    def process_step_finished(self, step_id: str, result: Optional[NamedTuple]):
        # get all information about the process step
        step = self.jssp.step_by_id[step_id]
        container = self.jssp.container_info_by_name[step.cont]
        # TODO: Insert custom thing to do after finishing a step.
        # custom kwargs given to steps (see mover_test for example) are also available in step.data
        if "read_barcode" in step.data:
            # TODO: Insert you own way to retrieve a barcode from a barcode reader
            container.barcode = f"Nice_Barcode{randint(1, 9999)}"
            # saves the barcode to the database.
            self.db_client.set_barcode(container)
        super().process_step_finished(step_id, result)

    def check_prerequisites(self, process: SMProcess) -> Tuple[bool, str]:
        message = ""
        # message = f"  Problems with starting {process.name}: \n"
        try:
            # try to create sila clients in advance
            needed_clients = set()
            for step in process.steps:
                # collect all devices that will be needed (including source and target)
                for needed in step.used_devices:
                    preference = needed.preferred
                    if preference:
                        needed_clients.add(preference)
                # check if the barcodereader is needed
                if isinstance(step, MoveStep):
                    if step.data.get("read_barcode", False):
                        needed_clients.add("BCReader")
            # these might not be explicitly marked as source in the first movement
            for cont in process.containers:
                needed_clients.add(cont.current_device)
            print("needed clients: ", needed_clients)
            # try client creation
            for device_name in needed_clients:
                if device_name in USE_REAL_SERVERS:
                    if not self.get_client(device_name, timeout=5):
                        message += f"Client creation for {device_name} failed.\n"
                    else:
                        print(f"created client for {device_name}")

            # connect the arm to all interacting devices
            if "PFonRail" in self.clients:
                arm_client: ArmClient = self.get_client("PFonRail")
                set_for_interaction = arm_client.ImplicitInteractionService.CurrentDeviceSet.get()
                # check if all interacting devices are set for implicit interaction
                interacting = needed_clients & interactive
                for device in interacting:
                    if device not in set_for_interaction:
                        message += f"{device} should be set for implicit interaction.\n"
                    else:
                        success = arm_client.ImplicitInteractionService.ConnectToDevice(
                            sila_server_name[device], Timeout=5).Success
                        if not success:
                            message += f"Failed to connect arm to {device}.\n"

            if message:
                message = f"Problems with starting {process.name}:\n {message}"
            else:
                message = "No Problems detected :-)\n"

            # TODO check all protocols exist
            # check whether robot interaction believes all used containers to the present?
        except Exception:
            logging.warning(f"proces prerequisite check for {process.name} failed\n{traceback.print_exc()}")
            message += f"proces prerequisite check for {process.name} failed\n{traceback.print_exc()}"
        return True, message

    def determine_destination_position(self, step: MoveStep) -> Optional[int]:
        # TODO change this to  customized positioning if necessary

        # checks the database for the free position with the lowest index
        return super().determine_destination_position(step)
