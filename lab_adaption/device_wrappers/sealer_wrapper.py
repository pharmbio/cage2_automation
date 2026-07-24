import logging
from laborchestrator.engine.worker_interface import Observable
from laborchestrator.structures import ProcessStep, ContainerInfo
from . import DeviceInterface
try:
    from sealer_server import Client as SealerClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as SealerClient
    logging.warning("sealer_server seems to be not installed")


class SealerWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(step: ProcessStep, labware: list[ContainerInfo], sila_client: SealerClient, **kwargs)\
        -> Observable:
        if step.function == "seal":
            temperature = step.data["temperature"]
            duration = step.data["duration"]
            logging.debug(f"Sealing at {temperature}°C for {duration}s")
            return sila_client.SealingController.Seal(Temperature=int(temperature), Time=int(duration))
        else:
            raise Exception(f"Unknown function {step.function}")
