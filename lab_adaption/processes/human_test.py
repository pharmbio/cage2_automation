"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess


class HumanTest(BasicProcess):
    def __init__(self):
        super().__init__(num_plates=1, process_name="HumanTest")

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i)

    def process(self):
        cont = self.containers[0]
        # simple request to allow the container to continue
        self.human.ask_for_ok(cont)
        # ask the human to assign some integer to the container.
        # This number can further be used for runtime decision making
        number = self.human.request_number(cont, message="Enter some demo number.")  # noqa: F841
        # tells the human to do a custom task
        self.human.do_task(cont, message="Put it in the freezer for 10 minutes")
