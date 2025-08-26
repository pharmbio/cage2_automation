import logging
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.structures import ProcessStep, ContainerInfo
from . import DeviceInterface
try:
    from sealer_server import Client as SealerClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as SealerClient
    logging.warning("sealer_server seems to be not installed")


class PlateSealerWrapper(DeviceInterface):
    def get_SiLA_handler(self, step: ProcessStep, cont: ContainerInfo, sila_client: SealerClient, **kwargs)\
        -> Observable:
        if step.function == "seal":
            return sila_client.ProtocolController.RunProtocol(ProtocolName="dummy_name")
        else:
            raise Exception(f"Unknown function {step.function}")
