"""
Duplicate this file and add/modify the missing parts to create new processes
"""

import logging

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess

try:
    from pylabrobot.agilent.biotek.lhc.enums.plates.plate_type import PlateType
    from pylabrobot.agilent.biotek.lhc.protocols.steps.steps import PeriDispense, PeriPrime
except ModuleNotFoundError:
    logging.warning("MultiflowTest will fail without pylabrobot's biotek lhc support being installed")


class MultiflowTest(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="MultiflowTest",
        )

    def create_resources(self):
        super().create_resources()
        # the dispenser works a 384 well plate -- its default, stated anyway
        self.containers[0].kwargs["plate_type"] = PlateType.PLATE_384_WELL

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)

    def process(self):
        # primes the secondary peri pump
        prime_step = PeriPrime(volume=300, flow_rate="High", peri_pump="Secondary")
        peri_dispense_step = PeriDispense(volume=10, flow_rate="High", peri_pump="Primary")
        cont = self.containers[0]
        #self.robot_arm.move(cont, self.dispenser, lidded=False)
        self.dispenser.execute_custom_steps(labware=cont, steps=[prime_step, peri_dispense_step])
        #self.robot_arm.move(cont, self.hotel2)
