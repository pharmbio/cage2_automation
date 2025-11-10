"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess
from lhc_python.steps import DispenseStep


class MultiflowTest(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="MultiflowTest",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)

    def process(self):
        steps = [
            DispenseStep()
        ]
        cont = self.containers[0]
        self.robot_arm.move(cont, self.dispenser)
        self.dispenser.execute_custom_steps(labware=cont, steps=steps)
        self.robot_arm.move(cont, self.hotel2)

