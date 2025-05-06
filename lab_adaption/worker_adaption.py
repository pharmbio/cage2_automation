"""

"""

from typing import Optional, NamedTuple, Dict, Any, Tuple
from laborchestrator.engine.worker_interface import WorkerInterface, Observable, DummyHandler
from laborchestrator.structures import SMProcess, MoveStep
from sila2.client import SilaClient
from .device_wrappers import(
    DeviceInterface,
    HumanWrapper,
    GreetingWrapper,
    GenericRobotArmWrapper,
)


# Out comment those you want to simulate the steps instead of calling an actual sila server
USE_REAL_SERVERS = [
    "GenericArm",
    "Human",
    "Greeter",
]

# maps the device names to the correct wrappers
device_wrappers: dict[str, type[DeviceInterface]] = dict(
    GenericArm=GenericRobotArmWrapper,
    Human=HumanWrapper,
    Greeter=GreetingWrapper,
)


class Worker(WorkerInterface):
    def execute_process_step(self, step_id: str, device: str, device_kwargs: Dict[str, Any]) -> Observable:
        print(f"Execute {step_id} on device {device}")
        # get all information about the process step
        step = self.jssp.step_by_id[step_id]
        cont = self.jssp.container_info_by_name[step.cont_names[0]]
        if device in USE_REAL_SERVERS:
            if isinstance(step, MoveStep):
                # create the client
                arm_client = self.get_client(device_name=device)

                origin_device = step.origin_device.name
                target_device = step.target_device.name
                origin_position = cont.current_pos  # the index of the position on the device
                target_position = step.destination_pos
                print(f"Will pick at {origin_device}{origin_position} and place at {target_device}{target_position}")
                # calls the sila server
                cmd_info = arm_client.RobotController.MovePlate(
                    OriginSite = (origin_device, origin_position),  # for example ("Hotel1", 3)
                    DestinationSite = (target_device, target_position),
                )
                # returns the ClientObservableCommandInstance for the move command
                return cmd_info
            if "Teleshake" in device:
                shaker_client = self.get_client(device_name=device)
                shaking_handler = ShakingHandler()
                # starts the execution
                shaking_handler.run_protocol(shaker_client, **device_kwargs, duration=step.duration)
                # return the handler for observation
                return shaking_handler
        handler = DummyHandler(4)
        handler.run_protocol(None)
        return handler

    def get_client(self, device_name) -> SilaClient | None:
        # use the device names of the lab_config.yaml
        # the ports might be different: adapt!
        if device_name == "XArm":
            return SilaClient(address="127.0.0.1", port=50052, insecure=True)
        #elif device_name == "Teleshake_1":
        #    return SilaClient(address="127.0.0.1", port=50053, insecure=True)
        #elif device_name == "Teleshake_2":
        #    return SilaClient(address="127.0.0.1", port=50054, insecure=True)
        return None

    def process_step_finished(self, step_id: str, result: Optional[NamedTuple]):
        super().process_step_finished(step_id, result)

    def check_prerequisites(self, process: SMProcess) -> Tuple[bool, str]:
        #TODO implement your custom steps here
        return True, "Nothing to report."

    def determine_destination_position(self, step: MoveStep) -> Optional[int]:
        #TODO change this to predefined positions if necessary

        # checks the database for the free position with the lowest index
        return super().determine_destination_position(step)