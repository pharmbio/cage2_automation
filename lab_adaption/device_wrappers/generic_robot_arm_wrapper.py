import logging

from laborchestrator.engine.worker_interface import Observable, ObservableProtocolHandler
from laborchestrator.structures import ContainerInfo, MoveStep

from .device_interface import DeviceInterface, finish
try:
    from genericroboticarm.sila_server import Client as ArmClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as ArmClient
    logging.warning("Generic robotic arm seems to be not installed")


class GenericRobotArmWrapper(DeviceInterface):
    def get_SiLA_handler(self, step: MoveStep, cont: ContainerInfo,
                         sila_client: ArmClient,
                         intermediate_actions: list[str] | None = None,
                         ) -> Observable:
        if intermediate_actions is None:
            intermediate_actions = []

        origin_site = (cont.current_device, cont.current_pos)
        target_site = (step.target_device.name, step.destination_pos)
        print(f"moving from {origin_site} to {target_site}")
        print(f"intermediate actions: {intermediate_actions}")

        class TransferHandler(ObservableProtocolHandler):
            def _protocol(self, client: ArmClient, **kwargs):
                pick_cmd = client.LabwareTransferManipulatorController.GetLabware(
                    HandoverPosition=(cont.current_device, cont.current_pos + 1),  # counting start at 1 there
                    IntermediateActions=intermediate_actions,
                )
                finish(pick_cmd)
                # this is thread blocking and not observable
                client.RobotController.PlacePlate(target_site)

        observable = TransferHandler()
        # starts _protocol and handles the status
        observable.run_protocol(sila_client)
        return observable
