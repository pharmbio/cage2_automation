"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess


class CytomatTest(BasicProcess):
    def __init__(self):
        super().__init__(
            # priority=5,  # change as needed
            num_plates=2,
            process_name="CytomatTest",
        )

    def init_service_resources(self):
        super().init_service_resources()
        self.containers[1].start_position("Cytomat", 0)
        self.containers[0].start_position("Hotel2", 1)

    def process(self):
        self.containers[1].wait_cost(100)
        self.robot_arm.move(self.containers[0], self.incubator1)
        self.robot_arm.move(self.containers[1], self.hotel2)
