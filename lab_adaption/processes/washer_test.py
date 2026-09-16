import logging

from lab_adaption.processes.basic_process import BasicProcess

try:
    from pylabrobot.agilent.biotek.lhc.enums.plates.plate_type import PlateType
    from pylabrobot.agilent.biotek.lhc.protocols.steps.step_parts.groups import Sectors
    from pylabrobot.agilent.biotek.lhc.protocols.steps.steps import (
        ManifoldDispense,
        ManifoldPrime,
        ManifoldWash,
    )
except ModuleNotFoundError:
    logging.warning("WasherTest will fail without pylabrobot's biotek lhc support being installed")


class WasherTest(BasicProcess):
    def __init__(self, priority=10):  # 0 has highest priority
        super().__init__(priority=priority, num_plates=1, process_name="WasherTest")

    def create_resources(self):
        super().create_resources()
        # the washer works a 384 well plate -- its default, stated anyway
        self.containers[0].kwargs["plate_type"] = PlateType.PLATE_384_WELL

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)

    def process(self):
        prime_step = ManifoldPrime(buffer="B", volume=10_000, flow_rate=5)
        wash_step = ManifoldWash(
            cycles=1,
            wash_format="Sector",
            sectors=Sectors([False, True, False, False]),
            dispense=ManifoldDispense(buffer="A", volume=50),
        )
        cont = self.containers[0]
        self.robot_arm.move(cont, self.washer, lidded=False)
        self.washer.execute_custom_steps(steps=[prime_step, wash_step], labware=cont)
        self.robot_arm.move(cont, self.hotel2)
