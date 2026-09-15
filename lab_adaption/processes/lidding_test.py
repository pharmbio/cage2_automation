"""
Tests the lidding: a lidded plate is unlidded on its way into Cytomat1, rests there for 30 seconds
and gets its lid back on when it returns to Hotel2.
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
        # the lid is parked in the lid storage while the plate is inside the cytomat
        self.robot_arm.move(self.containers[0], self.incubator1, lidded=False)
        # no temperature control, the plate simply rests inside
        self.incubator1.incubate(self.containers[0], duration=30, temperature=None)
        # the lid is picked up from its parking position again
        self.robot_arm.move(self.containers[0], self.hotel2, lidded=True)
