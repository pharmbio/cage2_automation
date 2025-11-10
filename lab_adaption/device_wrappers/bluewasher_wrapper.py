import traceback
import logging
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.structures import ProcessStep, ContainerInfo
from . import DeviceInterface
try:
    from bluewasher_sila.hardware_comm.commands import SimpleCommand, ComplexCommand
    from bluewasher_sila.hardware_comm.command_structure import program_to_str_list
except ModuleNotFoundError:
    logging.warning("The washer wrapper can not be used without lhc_python being installed.")
try:
    from bluewasher_sila import Client as BlueWasherClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as BlueWasherClient
    logging.warning("cell_washer seems to be not installed")


class BlueWasherWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(step: ProcessStep, cont: ContainerInfo, sila_client: BlueWasherClient, **kwargs)\
        -> Observable:
        if step.function == "custom_steps":
            try:
                # this should work and if not the exception should tell the problem
                protocol_steps = step.data["steps"]
                assert isinstance(protocol_steps, list)
                assert len(protocol_steps) > 0
                assert all(isinstance(elem, (SimpleCommand, ComplexCommand)) for elem in protocol_steps)
                content = program_to_str_list(protocol_steps)
                return sila_client.ProtocolExecutionService.ExecuteCustomProtocol(content)
            except Exception:
                raise Exception(traceback.print_exc())
        else:
            raise Exception(f"Unknown function {step.function}")
