"""
Example for wrapping multiple commands into an emulator of an observable sila command.
In _protocol() also non-sila API can be used. So, this also allows integration of non sila devices.
"""

import logging
import time

from laborchestrator.engine.worker_interface import ObservableProtocolHandler
from laborchestrator.structures import ProcessStep, ContainerInfo

try:
    from my_sila_server_package import Client as CustomClient
except ModuleNotFoundError:
    logging.warning("The sila server seems to not be installed")
    from sila2.client import SilaClient as CustomClient
from . import DeviceInterface


class CustomWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep, cont: ContainerInfo, sila_client: CustomClient, **kwargs
    ) -> ObservableProtocolHandler:
        my_custom_argument = step.data.get("my_key", None)

        # create an emulator for sila observable commands
        class GreetingHandler(ObservableProtocolHandler):
            response = "None"

            def _protocol(self, client, **kwargs):
                # implement you custom protocol here
                sila_client.MySilaFeature.MyNonObservableCommand(my_custom_argument)
                # wait if needed
                time.sleep(12)
                sila_client.MySilaFeature.OtherNonObservableCommand()
                # Optionally: provide some response
                self.response = sila_client.OtherSilaFeature.SayHello(cont.name)

            def get_responses(self):
                return self.response

        handler = GreetingHandler()

        # starts the protocol internally in a thread
        handler.run_protocol(client=None)
        # return the emulator
        return handler
