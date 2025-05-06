from laborchestrator.engine.worker_interface import ObservableProtocolHandler
from laborchestrator.structures import ProcessStep, ContainerInfo
from sila2.client import SilaClient
import time

from . import DeviceInterface


class GreetingWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(step: ProcessStep, cont: ContainerInfo, sila_client: SilaClient, **kwargs) -> ObservableProtocolHandler:
        class GreetingHandler(ObservableProtocolHandler):
            def _protocol(self, client, **kwargs):
                print("Hello world!")
                time.sleep(3)
                print("Goodbye!")

        handler = GreetingHandler()
        handler.run_protocol(client=None)
        return handler
