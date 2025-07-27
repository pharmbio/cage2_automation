import logging
from laborchestrator.engine.worker_interface import (
    Observable,
)
from laborchestrator.structures import ContainerInfo, ProcessStep

from . import DeviceInterface

try:
    from echo_server import Client as EchoClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as EchoClient

    logging.warning("Ech server seems to be not installed")


class EchoWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: EchoClient,
        **kwargs,
    ) -> Observable:
        if step.function == "execute_protocol":
            protocol = step.data.get("protocol", "")
            if not protocol:
                logging.warning(f"Protocol for step {step.name} not specified")
            logging.debug(f"Executing {protocol} on Echo")
            return sila_client.EchoProtocolController.ExecuteProtocol(
                ProtocolName = protocol,
            )