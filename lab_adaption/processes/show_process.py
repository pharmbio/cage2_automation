"""
Process with a diverse use of devices to showcase the cage2. 
Has no practical use ur biochemical background
"""

from lab_adaption.processes.basic_process import BasicProcess
from bluewasher_sila.hardware_comm.commands import Prime, Dispense, Centrifugation
import logging
from pathlib import Path
import pandas as pd

try:
    from lhc_python.steps.step_parts import PrimeInstructions, WashInstructions
    from lhc_python.steps.ewash_step import EMWashStep
    from lhc_python.steps.prime_step import PrimeStep
except ModuleNotFoundError:
    logging.warning("WasherTest will fail without lhc_python being installed")


class ShowProcess(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=10,
            process_name="ShowProcess",
        )

    def create_resources(self):
        super().create_resources()
        for plate in self.containers[4:8]:
            plate.lidded = False

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers[:4]):
            cont.set_start_position(self.hotel2, i)
        for i, cont in enumerate(self.containers[4:8]):
            cont.set_start_position(self.hotel2, i)
        for i, cont in enumerate(self.containers[8:10]):
            cont.set_start_position(self.incubator2, i)
            

    def process(self):
        paint_plates = self.containers[:4]
        dest_plates = self.containers[4:8]
        dest_barcodes = [f"PB000{i}" for i in range(146, 150)]
        source_plates = self.containers[8:10]
        source_barcodes = ["PB000164", "Copia Test"]
        # define the 405 washing steps
        wash_steps = [
            PrimeStep(instructions=PrimeInstructions(
                buffer_choice='B',
                volume=10,
                flow_rate=5,
                )),
            EMWashStep(settings=WashInstructions(
                num_cycles=1,
                wells_to_wash=[False, True, False, False],
                buffer_choice='A',
            ))
        ]
        multiflow_protocol = "dispensing.LHC"
        # create the bluewasher steps
        bluewash_steps = [
            Prime(channel=3, volume=10),
            Dispense(channel=3, volume=30),
            Centrifugation(duration_in_ms=5000, rpm=300)
        ]
        echo_protocol = Path(__file__).with_name("two_source_four_dest_echo_protocol.csv")
        dataframe = pd.read_csv(echo_protocol)
        for cont in paint_plates:
            self.robot_arm.move(cont, self.incubator1, read_barcode=True)
            self.incubator1.incubate(cont, temperature=37, duration=20*60)
            self.robot_arm.move(cont, self.washer, lidded=False)
            self.washer.execute_custom_steps(labware=cont, steps=wash_steps)
            self.robot_arm.move(cont, self.hotel2, lidded=True)
            cont.min_wait(20*60)
            self.robot_arm.move(cont, self.dispenser, lidded=False)
            self.dispenser.run_protocol(protocol=multiflow_protocol, labware=cont)
            self.robot_arm.move(cont, self.bluewasher, lidded=False)
            self.bluewasher.execute_custom_steps(labware=cont, steps=bluewash_steps)
            self.robot_arm.move(cont, self.incubator2, lidded=True)

        # echo-process mit 2 source und 4 destination platten (eine braucht beide source) und anschließend in den Sealer
        # source_plates from cytomat2, destination from hotel2 end in cytomat2
        for i in range(len(source_plates)):
            source_plate = source_plates[i]
            source_bc = source_barcodes[i]
            self.robot_arm.move(source_plate, self.echo, role="source", lidded=False)
            source_plate.wait_cost(20)
            # only survey the necessary part of this source plate
            source_dataframe = dataframe[(dataframe["Source plate"] == source_bc)]
            self.echo.survey_for_protocol(source_plate=source_plate, protocol=source_dataframe)
            source_plate.wait_cost(20)
            for j in range(len(dest_plates)):
                dest_plate = dest_plates[j]
                dest_bc = dest_barcodes[j]
                # extract the transfers from source_plate to dest_plate
                partial_df = dataframe[(dataframe["Source plate"] == source_bc) &
                                       (dataframe["Destination plate"] == dest_bc)]
                num_transfers = len(partial_df)
                # only execute if there is anything to transfer between those plates
                if num_transfers > 0:
                    self.robot_arm.move(dest_plate, self.echo, role="destination")
                    dest_plate.wait_cost(20)
                    self.echo.execute_transfer_protocol(source_plate, dest_plate, partial_df)
                    dest_plate.wait_cost(20)
                    if i==0 and j==2:
                        self.robot_arm.move(dest_plate, self.hotel2)
            self.robot_arm.move(source_plate, self.incubator2, lidded=True)
        for  dest_plate in dest_plates:
            self.robot_arm.move(dest_plate, self.sealer)
            self.sealer.seal_plate(dest_plate)
            self.robot_arm.move(dest_plate, self.incubator2)     
