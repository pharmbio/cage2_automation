"""
Example for wrapping a single observable sila command
"""

import logging

from sila2.client import ClientObservableCommandInstance
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
    ) -> ClientObservableCommandInstance:
        my_custom_argument = step.data.get("my_key", None)
        if not my_custom_argument:
            logging.error("necessary argument my_key not given")
        observable_cmd = sila_client.MySilaFeature.MyObservableCommand()
        return observable_cmd
