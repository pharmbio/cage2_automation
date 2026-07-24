"""
Small process to test the sealer device. It moves a plate from the hotel to the sealer, seals it and moves it back to the hotel.
"""

from lab_adaption.processes.basic_process import BasicProcess


class SealerTest(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="SealerTest",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)

    def process(self):
        cont = self.containers[0]
        self.robot_arm.move(cont, self.sealer, lidded=False)
        self.sealer.seal_plate(labware=cont, temperature=150, duration=13)
        self.robot_arm.move(cont, self.hotel2, lidded=True)
