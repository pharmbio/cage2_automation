import logging

from lab_adaption.processes.basic_process import BasicProcess
try:
    from lhc_python.steps.step_parts import CWFlowRate, WashInstructions
    from lhc_python.steps.ewash_step import EMWashStep
except ModuleNotFoundError:
    logging.warning("Test will fail without lhc_python being installed")


class WasherTest(BasicProcess):
    def __init__(self, priority=10):  # 0 has highest priority
        super().__init__(priority=priority, num_plates=1, process_name="WasherTest")

    def create_resources(self):
        super().create_resources()

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        self.containers[0].set_start_position(self.washer, 0)

    def process(self):
        step = EMWashStep()
        step.create(settings = WashInstructions(
            num_cycles=1,
            wells_to_wash=[False, True, False, False],
            buffer_choice='A',
        ))
        self.washer.execute_custom_steps(steps=[step], labware=self.containers[0])
