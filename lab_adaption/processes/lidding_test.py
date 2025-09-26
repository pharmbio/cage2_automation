"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess


class LiddingTest(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="LiddingTest",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel2, i)

    def process(self):
        self.robot_arm.move(self.containers[0], self.hotel1, lidded=False)
        self.robot_arm.move(self.containers[0], self.hotel2, lidded=True)
