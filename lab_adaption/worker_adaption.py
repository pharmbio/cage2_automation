"""

"""

from typing import Optional, NamedTuple, Dict, Any, Tuple
from laborchestrator.engine.worker_interface import WorkerInterface, Observable, DummyHandler
from laborchestrator.structures import SMProcess, MoveStep


class Worker(WorkerInterface):
    def execute_process_step(self, step_id: str, device: str, device_kwargs: Dict[str, Any]) -> Observable:
        print(f"Execute {step_id} on device {device}")
        handler = DummyHandler(4)
        handler.run_protocol(None)
        return handler


    def process_step_finished(self, step_id: str, result: Optional[NamedTuple]):
        super().process_step_finished(step_id, result)

    def check_prerequisites(self, process: SMProcess) -> Tuple[bool, str]:
        #TODO implement your custom steps here
        return True, "Nothing to report."

    def determine_destination_position(self, step: MoveStep) -> Optional[int]:
        #TODO change this to predefined positions if necessary

        # checks the database for the free position with the lowest index
        return super().determine_destination_position(step)