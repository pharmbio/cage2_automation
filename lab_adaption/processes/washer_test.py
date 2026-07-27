import logging

from lab_adaption.processes.basic_process import BasicProcess
try:
    from lhc_python.steps.step_parts import PrimeInstructions, WashInstructions
    from lhc_python.steps.ewash_step import EMWashStep
    from lhc_python.steps.prime_step import PrimeStep
except ModuleNotFoundError:
    logging.warning("WasherTest will fail without lhc_python being installed")


class WasherTest(BasicProcess):
    def __init__(self, priority=10):  # 0 has highest priority
        super().__init__(priority=priority, num_plates=1, process_name="WasherTest")

    def create_resources(self):
        super().create_resources()

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.hotel2, 0)

    def process(self):
        prime_step = PrimeStep(instructions=PrimeInstructions(
            buffer_choice='B',
            volume=10,
            flow_rate=5,
            ))
        wash_step = EMWashStep(settings = WashInstructions(
            num_cycles=1,
            wells_to_wash=[False, True, False, False],
            buffer_choice='A',
        ))
        cont = self.containers[0]
        self.robot_arm.move(cont, self.washer, lidded=False)
        self.washer.execute_custom_steps(steps=[prime_step, wash_step], labware=cont)
        self.robot_arm.move(cont, self.hotel2)
