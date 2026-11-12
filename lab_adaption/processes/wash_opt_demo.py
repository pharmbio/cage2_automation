"""
Washing optimization demo on Squid2: coverage check, 3 x (BlueWasher wash + well empty check), coverage check.
The plate starts in Hotel2 and is put back there at the end.
"""

from lab_adaption.processes.basic_process import BasicProcess
from bluewasher_sila.hardware_comm.commands import Prime, Dispense, Centrifugation

N_WASHES = 3
SQUID_PROJECT = "washing_optimization"
COVERAGE_CHECK = "5minutetest.json"
WELL_EMPTY_CHECK = "demo_empty_check.json"


class WashOptDemo(BasicProcess):
    def __init__(self):
        super().__init__(
            num_plates=1,
            process_name="WashOptDemo",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)

    def process(self):
        # same steps as interface_service/examples/generated_protocol.prog
        wash_protocol = [
            Prime(channel=4, volume=20),
            Dispense(channel=4, volume=87, pressure=1),
            Centrifugation(duration_in_ms=8000, rpm=-950, acceleration=400, deceleration=300),
            Centrifugation(duration_in_ms=12000, rpm=1150, acceleration=500, deceleration=800),
        ]
        cont = self.containers[0]
        self.robot_arm.move(cont, self.squid2, lidded=False, read_barcode=True)
        self.squid2.run_protocol(labware=cont, protocol=COVERAGE_CHECK, project=SQUID_PROJECT)
        for _ in range(N_WASHES):
            self.robot_arm.move(cont, self.bluewasher, lidded=False)
            self.bluewasher.execute_custom_steps(labware=cont, steps=wash_protocol)
            self.robot_arm.move(cont, self.squid2, lidded=False)
            self.squid2.run_protocol(labware=cont, protocol=WELL_EMPTY_CHECK, project=SQUID_PROJECT)
        self.squid2.run_protocol(labware=cont, protocol=COVERAGE_CHECK, project=SQUID_PROJECT)
        self.robot_arm.move(cont, self.hotel2, lidded=True)
