"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from pythonlab.resource import DynamicLabwareResource as ReagentResource  # noqa: F401
from lab_adaption.processes.basic_process import BasicProcess
import pandas as pd


num_source = 3
num_dest = 4


class BigEchoProtocol(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=num_source + num_dest,
            process_name="BigEchoProcess",
        )

    def create_resources(self):
        super().create_resources()
        self.source_plates = self.containers[:num_source]
        self.dest_plates = self.containers[num_source:]
        for plate in self.source_plates:
            plate.kwargs["plate_type"] = "384PP_DMSO2"
        for plate in self.dest_plates:
            plate.kwargs["plate_type"] = "384PP_Dest"

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.source_plates):
            cont.set_start_position(self.hotel1, i)
        for i, cont in enumerate(self.dest_plates):
            cont.set_start_position(self.hotel2, i)

    def process(self):
        protocol_path = "~/workspace/devices/uppsala/echo/sila_server/tests/test_data/3source_4dest_test.csv"
        dataframe = pd.read_csv(protocol_path)
        source_barcodes = list(set(dataframe["Source plate"]))
        dest_barcodes = list(set(dataframe["Destination plate"]))

        # make sure we have the correct plates
        all_barcodes = source_barcodes + dest_barcodes
        for i in range(num_source + num_dest):
            plate = self.containers[i]
            # only reads the barcode and puts it back
            self.robot_arm.move(plate, plate.start_position.resource, read_barcode=True,
                                assumed_barcode=all_barcodes[i])

        for i in range(num_source):
            source_plate = self.source_plates[i]
            source_bc = source_barcodes[i]
            self.robot_arm.move(source_plate, self.echo, role="source")
            source_plate.wait_cost(20)
            # only survey the necessary part of this source plate
            source_dataframe = dataframe[(dataframe["Source plate"] == source_bc)]
            self.echo.survey_for_protocol(source_plate=source_plate, protocol=source_dataframe)
            source_plate.wait_cost(20)
            for j in range(num_dest):
                dest_plate = self.dest_plates[j]
                dest_bc = dest_barcodes[j]
                # extract the transfers from source_plate to dest_plate
                partial_df = dataframe[(dataframe["Source plate"] == source_bc) &
                                       (dataframe["Destination plate"] == dest_bc)]
                num_transfers = len(partial_df)
                # only execute if there is anything to transfer between those plates
                if num_transfers > 0:
                    self.robot_arm.move(dest_plate, self.echo, role="destination")
                    self.echo.execute_transfer_protocol(source_plate, dest_plate, partial_df)
                    self.robot_arm.move(dest_plate, self.hotel2)
                source_plate.wait_cost(20)
            self.robot_arm.move(source_plate, self.hotel1)


