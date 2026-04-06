"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess


class CellPaintingMalin(BasicProcess):
    def __init__(self):
        super().__init__(
            priority=0,
            num_plates=8,
            process_name="CellPainting",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.incubator1, i)

    def process(self):
        incubation_time = 15*60  # in seconds
        blue_washer_protocol1 = ""
        blue_washer_protocol2 = ""
        dispenser_protocol1 = ""
        dispenser_protocol2 = ""
        dispenser_protocol3 = ""

        for cont in self.containers:
            self.robot_arm.move(cont, self.dispenser, lidded=False)
            self.dispenser.run_protocol(protocol=dispenser_protocol1, labware=cont, duration=120)
            self.robot_arm.move(cont, self.incubator1, lidded=True)

            self.incubator1.incubate(cont, duration=incubation_time, temperature=37)

            self.robot_arm.move(cont, self.dispenser, lidded=False)
            self.dispenser.run_protocol(protocol=dispenser_protocol2, labware=cont, duration=120)
            self.robot_arm.move(cont, self.incubator1, lidded=True)

            self.incubator1.incubate(cont, duration=incubation_time, temperature=37)

            self.robot_arm.move(cont, self.bluewasher, lidded=False)
            self.bluewasher.run_protocol(protocol=blue_washer_protocol1, labware=cont, duration=120)
            self.robot_arm.move(cont, self.dispenser, lidded=False)
            self.dispenser.run_protocol(protocol=dispenser_protocol3, labware=cont, duration=120)
            self.robot_arm.move(cont, self.incubator1, lidded=True)

            self.incubator1.incubate(cont, duration=incubation_time, temperature=37)

            self.robot_arm.move(cont, self.bluewasher, lidded=False)
            self.bluewasher.run_protocol(protocol=blue_washer_protocol2, labware=cont, duration=120)
            self.robot_arm.move(cont, self.hotel2, lidded=True)
