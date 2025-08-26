import logging
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.structures import ProcessStep, ContainerInfo
from . import DeviceInterface

try:
    from microscope_server import Client as SquidClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as SquidClient
    logging.warning("microscope_server seems to be not installed")


class SquidWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(step: ProcessStep, cont: ContainerInfo, sila_client: SquidClient, **kwargs) -> Observable:
        protocol = step.data["protocol"]
        return sila_client.ProtocolController.RunProtocol(protocol)
