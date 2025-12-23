"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess
from bluewasher_sila.hardware_comm.commands import Prime, Dispense, Centrifugation


class BlueWasherTest(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="BlueWasherTest",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)

    def process(self):
        protocol = [
            Prime(channel=3, volume=10),
            Dispense(channel=3, volume=30),
            Centrifugation(duration_in_ms=5000, rpm=300)
        ]
        cont = self.containers[0]
        self.robot_arm.move(cont, self.bluewasher, lidded=False)
        self.bluewasher.execute_custom_steps(labware=cont, steps=protocol)
        self.robot_arm.move(cont, self.hotel2)

