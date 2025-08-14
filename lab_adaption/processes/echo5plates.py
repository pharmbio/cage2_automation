"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess


class Echo5Plates(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=3,
            process_name="Echo5Plates",
        )

    def create_resources(self):
        super().create_resources()
        # self.lysate = ReagentResource(proc=self, name=f"Lysate", filled=True, outside_cost=20, priority=10)
        self.source_plate = self.containers[0]
        self.target_plates = self.containers[1:]
        # set the plate types
        for cont in self.target_plates:
            cont.kwargs["plate_type"] = "384PP_Dest"
        self.source_plate.kwargs["plate_type"] = "384PP_DMSO2"

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.target_plates):
            cont.set_start_position(self.hotel2, i)
        self.source_plate.set_start_position(self.hotel1, 0)

    def process(self):
        protocol = r"C:\users\pharmbio\Desktop\Malin\CP_Echo_files\0000_test.csv"
        self.robot_arm.move(self.source_plate, self.echo, role="source", read_barcode=True)
        #for plate in self.target_plates:
        #    self.robot_arm.move(plate, self.echo, role="destination", read_barcode=True)
        #    self.echo.execute_transfer_protocol(protocol, self.source_plate, plate)
        #    self.robot_arm.move(plate, self.hotel2)
        self.robot_arm.move(self.source_plate, self.hotel1)