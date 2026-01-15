""" """

import logging
import traceback
from datetime import datetime
from typing import Optional, NamedTuple, Dict, Any, Tuple
from random import randint

from laborchestrator.database_integration import StatusDBInterface
from laborchestrator.engine import ScheduleManager
from laborchestrator.engine.worker_interface import (
    WorkerInterface,
    Observable,
    DummyHandler,
)
from laborchestrator.structures import SMProcess, MoveStep, SchedulingInstance, ProcessStep
from sila2.client import SilaClient

from .device_wrappers import (
    DeviceInterface,
    HumanWrapper,
    GenericRobotArmWrapper,
    EchoWrapper,
    LabwareTransferHandler,
    WasherDispenserWrapper,
    SquidWrapper,
    PlateSealerWrapper,
    BlueWasherWrapper,
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
    "BCReader",
    "Washer",
    "Cytomat1",
    "Cytomat2",
    "BlueWasher",
    "MultiFlow",
]
interactive = {"Echo", "Washer", "Sealer", "Cytomat1", "BlueWasher", "MultiFlow"}

# maps the device names (from the platform_config and process description) to the correct wrappers
device_wrappers: dict[str, type[DeviceInterface]] = dict(
    #PFonRail=GenericRobotArmWrapper,
    PFonRail=LabwareTransferHandler,
    Human=HumanWrapper,
    Echo=EchoWrapper,
    Echo_sim=EchoWrapper,
    Washer=WasherDispenserWrapper,
    MultiFlow=WasherDispenserWrapper,
    BlueWasher=BlueWasherWrapper,
)

# maps the device names (from the platform_config and process description) to the correct sila server names
# those without a sila server can be left out
sila_server_name: dict[str, str] = dict(
    PFonRail="PFonRail",
    Echo="Echo",
    Human="Human",
    BCReader="BCReader",
    Echo_sim="EchoSim",
    Cytomat1="Cytomat1",
    Cytomat2="Cytomat2",
    Washer="Washer",
    BlueWasher="BlueWasher",
    MultiFlow="MultiFlow",
)
LID_STORAGE ="Hotel2"

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
        self.barcode_list = []

    def update_information_from_db(self, step: ProcessStep):
        # try to update the runtime container info from the database
        for cont_name in reversed(step.cont_names):
            try:
                cont = self.jssp.container_info_by_name[cont_name]
                # first try to find the info by barcode
                cont_info = self.db_client.get_cont_info_by_barcode(cont.barcode)
                if not cont_info:
                    # if the barcode failed, try to find the information by location
                    cont_info = self.db_client.get_container_at_position(cont.current_device, cont.current_pos)
                    logging.info("found container by its position")
                    if cont_info.barcode not in [None, "None"]:
                        logging.info(f"Taking barcode {cont_info.barcode} from database replacing {cont.barcode}")
                    if not cont_info:
                        cont_info = cont
                # copy information to the runtime environment. The database is considered more reliable
                cont.barcode = cont_info.barcode
                cont.current_pos = cont_info.current_pos
                cont.current_device = cont_info.current_device
                cont.lidded = cont_info.lidded
                cont.lid_site = cont_info.lid_site
                cont.filled = cont_info.filled
            except Exception as ex:
                logging.error(f"Failed to retrieve container information from db: {ex}")

    def execute_process_step(
        self, step_id: str, device: str, device_kwargs: Dict[str, Any]
    ) -> Observable:
        print(f"Execute {step_id} on device {device}")
        # get all information about the process step
        step = self.jssp.step_by_id[step_id]
        cont = self.jssp.container_info_by_name[step.cont_names[0]]
        self.update_information_from_db(step)
        if device in USE_REAL_SERVERS:
            # TODO remove when working with real echo
            # switch to simulation for protocol execution
            #if device == "Echo":
            #    device += "_sim"
            client = self.get_client(device_name=device)
            if client:
                wrapper = device_wrappers[device]
                if isinstance(step, MoveStep):
                    # provide the sila clients if current and/or target device implement interactive transfer
                    if cont.current_device in interactive:
                        device_kwargs["interactive_source"] =\
                            self.get_client(cont.current_device).LabwareTransferSiteController
                    if step.target_device.name in interactive:
                        device_kwargs["interactive_target"] =\
                            self.get_client(step.target_device.name).LabwareTransferSiteController
                    # just add it, so the following lines can add actions without KeyError
                    if "intermediate_actions" not in device_kwargs:
                        device_kwargs["intermediate_actions"] = []
                    if step.data.get("read_barcode", False):
                        print("The arm is supposed to read the barcode now.")
                        device_kwargs["intermediate_actions"].append("read_barcode")
                        bc_client = self.get_client("BCReader")
                        # just to be sure not to produce an exception
                        if bc_client:
                            self.barcode_list = bc_client.BarcodeReaderService.AllBarcodes.get()
                    # check whether its specified whether the lid must be on in the target position
                    desired_lidding_state = step.data.get("lidded", None)
                    if desired_lidding_state is not None:
                        # check whether the desired state is already there
                        if not desired_lidding_state == cont.lidded:
                            if not desired_lidding_state:
                                next_free_slot = next(
                                    (slot for slot in self.db_client.get_all_positions(LID_STORAGE)
                                    if self.db_client.position_empty(LID_STORAGE, slot)),
                                    None)
                                if next_free_slot is None:
                                    logging.error("There is no free slot in the lid storage")
                                lidding_cmd = f"unlid_{LID_STORAGE}_{next_free_slot}"
                                # store the information for later
                                step.data["lid_target"] = [LID_STORAGE, next_free_slot]
                            else:
                                # put on the lid
                                lid_position = cont.lid_site
                                if lid_position is None:
                                    logging.error(f"position of lid of {cont} is undefined")
                                lidding_cmd = f"lid_{lid_position[0]}_{lid_position[1]}"
                            device_kwargs["intermediate_actions"].append(lidding_cmd)
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
                    server_name=server_name, timeout=timeout, insecure=True,
                )
                self.clients[device_name] = client
                return client
            except TimeoutError as error:
                logging.exception(f"Could not connect to {server_name}:\n{error}")
        return None

    def process_step_finished(self, step_id: str, result: Optional[NamedTuple]):
        # get all information about the process step
        step = self.jssp.step_by_id[step_id]
        labware = self.jssp.container_info_by_name[step.cont]
        if step.data.get("read_barcode", False):
            print("We did read a barcode during the move")
            bc_reader_client = self.get_client("BCReader")
            if bc_reader_client:
                current_bc_list = bc_reader_client.BarcodeReaderService.AllBarcodes.get()
                if len(self.barcode_list) == len(current_bc_list):
                    barcode = f"Grumpycat_{randint(0, 99999)}"
                    logging.warning(
                        f"{datetime.now()}: Seems like barcode reading failed. Generated random barcode {barcode}")
                else:
                    barcode = bc_reader_client.BarcodeReaderService.LastBarcode.get()
                    print(f"barcode is {barcode}")
                labware.barcode = barcode
                self.db_client.set_barcode(labware)
        if step.data.get("lidded", False):
            self.db_client.lidded_container(labware, None, None)
        if step.data.get("lid_target", None):
            self.db_client.unlidded_container(labware, *step.data["lid_target"])
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
                # check if the barcode reader is needed
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
        if step.target_device.name == "Echo":
            labware_role = step.data.get("role", "")
            print(f"labware role is {labware_role}")
            if not labware_role:
                logging.warning(f"Role of plate going into Echo not specified in step {step.name}."
                                f" Assuming next free position")
            if labware_role == "source":
                return 0
            elif labware_role == "destination":
                return 1
        # checks the database for the free position with the lowest index
        return super().determine_destination_position(step)
