"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess


class ShowProcess(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=4,
            process_name="ShowProcess",
        )

    def create_resources(self):
        super().create_resources()

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.hotel2, i)

    def process(self):
        paint_cont = self.containers[:4]
        wash_steps = [

        ]
        bluewash_steps = [

        ]
        for cont in paint_cont:
            self.robot_arm.move(cont, self.incubator1, read_barcode=True)
            self.incubator1.incubate(cont, temperature=37, duration=20*60)
            self.robot_arm.move(cont, self.washer, lidded=False)
            self.washer.execute_custom_steps(labware=cont, steps=wash_steps)
            self.robot_arm.move(cont, self.hotel2, lidded=True)
            cont.min_wait(20*60)
            self.robot_arm.move(cont, self.bluewasher, lidded=False)
            self.bluewasher.execute_custom_steps(labware=cont, steps=bluewash_steps)
            self.robot_arm.move(cont, self.incubator2, lidded=True)