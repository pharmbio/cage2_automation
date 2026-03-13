"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess


# todo change process name
class MyProcess(BasicProcess):
    def __init__(self):
        # todo change platenumber and name
        super().__init__(
            # priority=5,  # change as needed
            num_plates=4,
            process_name="MyProcess",
        )

    def init_service_resources(self):
        # setting start position of containers
        # todo change the starting position. default is the first [num_plates] slots in Hotel1
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel1, i)

    def process(self):
        # todo: fill in the actual process
        pass
