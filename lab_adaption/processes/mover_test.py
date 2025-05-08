"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess


class MoverTest(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="MoverTest"
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(
                self.hotel1, i)

    def process(self):
        # the orchestrator will assign the first free(according to the database) position within hotel2
        self.robot_arm.move(self.containers[0], target_loc=self.hotel2)
        # we can give custom kwargs which will appear in WorkerInterface.execute_process_step in device_kwargs
        self.robot_arm.move(self.containers[0], target_loc=self.hotel3, read_barcode=True)




