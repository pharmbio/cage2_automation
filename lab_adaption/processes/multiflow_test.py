"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess
from lhc_python.steps.step_interface import DemoStep


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
        # primes the secondary peri pump
        prime_step = DemoStep(name="prime_demo", step_def="DV103|2|True|300|3|High|True|0|2", body="")
        peri_dispense_step = DemoStep(name="peri_dispense_demo", step_def="DV103|1|10|High|0|333|0|0|True|10|2|111111111111111111111111111111111111111111111111|1111|1", body="")
        cont = self.containers[0]
        #self.robot_arm.move(cont, self.dispenser, lidded=False)
        self.dispenser.execute_custom_steps(labware=cont, steps=[prime_step])
        #self.robot_arm.move(cont, self.hotel2)

