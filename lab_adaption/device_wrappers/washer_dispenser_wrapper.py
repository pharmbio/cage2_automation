import traceback
import logging
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.structures import ProcessStep, ContainerInfo
from . import DeviceInterface
try:
    from lhc_python.steps.step_interface import Step
except ModuleNotFoundError:
    logging.warning("The washer wrapper can not be used without lhc_python being installed.")
try:
    from cell_washer import Client as WasherDispenserClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as WasherDispenserClient
    logging.warning("cell_washer seems to be not installed")


class WasherDispenserWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(step: ProcessStep, cont: ContainerInfo, sila_client: WasherDispenserClient, **kwargs)\
        -> Observable:
        # TODO find better naming in pythonlab
        if step.function in ["fix_cells", "wash_cells"]:
            protocol = step.data['protocol']
            return sila_client.ProtocolExecutionService.ExecuteProtocol(ProtocolName=protocol)
        elif step.function == "custom_steps":
            try:
                # this should work and if not the exception should tell the problem
                protocol_steps = step.data["steps"]
                assert isinstance(protocol_steps, list)
                assert len(protocol_steps) > 0
                assert all(isinstance(elem, Step) for elem in protocol_steps)
                # compress step definitions to strings
                step_definitions = [
                    step_definition.to_string()
                    for step_definition in protocol_steps
                ]
                # check if the expected function is available in the sever
                assert hasattr(sila_client, "ProtocolExecutionService")
                cmd = sila_client.ProtocolExecutionService.ExecuteCustomProtocol(step_definitions)

                return cmd
            except Exception:
                raise Exception(traceback.print_exc())
        else:
            raise Exception(f"Unknown function {step.function}")
