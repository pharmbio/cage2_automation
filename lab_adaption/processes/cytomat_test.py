"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess


class CytomatTest(BasicProcess):
    def __init__(self):
        super().__init__(
            priority=10,
            num_plates=2,
            process_name="CytomatTest",
        )

    def init_service_resources(self):
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)
        self.containers[1].set_start_position(self.incubator1, 0)

    def process(self):
        self.containers[1].wait_cost(100)
        self.robot_arm.move(self.containers[0], self.incubator1)
        self.robot_arm.move(self.containers[1], self.hotel2)
