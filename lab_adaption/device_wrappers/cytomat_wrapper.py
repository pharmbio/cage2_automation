"""
Wrapper for the two Cytomat2C incubators of cage 2. In contrast to the Greifswald cytomats,
these have no shaker, so a requested shaking frequency is ignored.
"""

import logging
import time
from datetime import timedelta

from laborchestrator.engine.worker_interface import Observable, ObservableProtocolHandler
from laborchestrator.structures import ContainerInfo, ProcessStep

from . import DeviceInterface

try:
    from cytomat2C_server import Client as CytomatClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as CytomatClient

    logging.warning("cytomat2C_server seems to be not installed")

# The same tolerance the cytomat server uses to decide that a target temperature is reached
TEMPERATURE_TOLERANCE = 0.5


class IncubationHandler(ObservableProtocolHandler):
    """
    Incubating is nothing the cytomat can be commanded to do: the plate simply stays inside until the
    process moves it out again. This handler therefore makes sure the temperature is controlled and
    then waits for the incubation duration.
    """

    def __init__(self, step: ProcessStep):
        super().__init__()
        # the reader puts the incubation time into the step duration, the data entry stays empty
        self.duration = step.data.get("duration") or step.duration
        self.temperature = step.data.get("temperature", None)
        self.start = None

    def _protocol(self, client: CytomatClient, **kwargs):
        self.start = time.time()
        command = self._control_temperature(client) if self.temperature is not None else None
        # the plate just rests inside for the remaining time
        time.sleep(max(0.0, self.duration - (time.time() - self.start)))
        # The temperature control can take much longer than the incubation (roughly 10 minutes per kelvin).
        # It must not extend this step, so it is only reported and then left running on the cytomat.
        if command is not None and not command.done:
            logging.warning(
                f"The cytomat did not reach {self.temperature} within the {self.duration}s of incubation."
                f" It keeps controlling the temperature in the background.",
            )
            try:
                command.cancel_execution_info_subscription()
            except Exception as ex:  # noqa: BLE001
                logging.debug(f"Could not unsubscribe from the temperature control command: {ex}")

    def _control_temperature(self, client: CytomatClient):
        try:
            current_temperature = client.TemperatureController.CurrentTemperature.get()
        except Exception as ex:  # noqa: BLE001
            logging.warning(f"Could not read the current temperature of the cytomat: {ex}")
            current_temperature = None
        if current_temperature is not None and abs(current_temperature - self.temperature) <= TEMPERATURE_TOLERANCE:
            logging.debug(f"Cytomat is already at {current_temperature}. No temperature control needed.")
            return None
        # ControlTemperature only finishes once the target is reached, so it is started without waiting for it
        logging.info(f"Setting the cytomat temperature to {self.temperature} (currently {current_temperature})")
        return client.TemperatureController.ControlTemperature(TargetTemperature=self.temperature)

    def get_remaining_time(self) -> timedelta:
        if self.start is None:
            return timedelta(seconds=self.duration)
        return timedelta(seconds=max(0.0, self.duration - (time.time() - self.start)))


class Cytomat2CWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        labware: list[ContainerInfo],
        sila_client: CytomatClient,
        **kwargs,
    ) -> Observable:
        if step.function == "incubate":
            handler = IncubationHandler(step)
            handler.run_protocol(sila_client)
            return handler
        elif step.function == "control_temperature":
            return sila_client.TemperatureController.ControlTemperature(
                TargetTemperature=step.data["temperature"],
            )
        else:
            raise Exception(f"Unknown function {step.function}")
