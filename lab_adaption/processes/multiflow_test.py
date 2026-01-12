"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess
from lhc_python.steps import DispenseStep, PrimeStep


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
        step = PrimeStep()
        step.step_data = "DV103|4|1|50|2|333|-4|-4|True|50|2|7|111111111111111111111111111111111111111111111111|1|1111"
        cont = self.containers[0]
        #self.robot_arm.move(cont, self.dispenser, lidded=False)
        self.dispenser.execute_custom_steps(labware=cont, steps=[step])
        #self.robot_arm.move(cont, self.hotel2)

