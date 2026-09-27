"""
Moves four unlidded plates into the four squids, runs 5minutetest.json on each and moves them back to the hotel.
"""

from lab_adaption.processes.basic_process import BasicProcess


class SquidDemo(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=4,
            process_name="SquidDemo",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.lidded = False
            cont.set_start_position(self.hotel1, i)
        self.squids = [self.squid1, self.squid2, self.squid3, self.squid4]

    def process(self):
        for i in range(4):
            self.robot_arm.move(self.containers[i], self.squids[i], read_barcode=True)
            self.squids[i].run_protocol(labware=self.containers[i], protocol="5minutetest.json", duration=5*60, project="trash")
            self.robot_arm.move(self.containers[i], self.hotel1)
