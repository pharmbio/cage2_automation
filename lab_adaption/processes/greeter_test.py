"""
Duplicate this file and add/modify the missing parts to create new processes
"""


from lab_adaption.processes.basic_process import BasicProcess


class GreeterTest(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="GreeterTest"
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(
                self.hotel1, i)

    def process(self):
        self.greeter.wave(self.containers[0])



