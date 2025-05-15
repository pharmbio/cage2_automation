import logging

from laborchestrator.engine.worker_interface import ObservableProtocolHandler
from laborchestrator.structures import ProcessStep, ContainerInfo

try:
    from sila2_example_server import Client as GreeterClient
except ModuleNotFoundError:
    logging.warning("The sila example server seems to not be installed")
    from sila2.client import SilaClient as GreeterClient
from . import DeviceInterface


class GreetingWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep, cont: ContainerInfo, sila_client: GreeterClient, **kwargs
    ) -> ObservableProtocolHandler:
        # since GreetingProvider.SayHello is no observable command, we have to wrap in into an ObservableProtocolHandler
        class GreetingHandler(ObservableProtocolHandler):
            response = "None"

            def _protocol(self, client, **kwargs):
                self.response = sila_client.GreetingProvider.SayHello(cont.name)

            def get_responses(self):
                return self.response.Greeting

        handler = GreetingHandler()
        handler.run_protocol(client=None)
        return handler
