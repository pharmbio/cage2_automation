import logging
from threading import Thread

from laborchestrator.engine.worker_interface import (
    Observable,
    ObservableProtocolHandler,
)
from laborchestrator.structures import ContainerInfo, MoveStep
from sila2.framework import CommandExecutionStatus

from . import DeviceInterface, finish_observable_command
from .labware_site import LabwareSite, Site

try:
    from genericroboticarm.sila_server import Client as ArmClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as ArmClient, SilaClient

    logging.warning("Generic robotic arm seems to be not installed")


class GenericRobotArmWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: MoveStep,
        cont: ContainerInfo,
        sila_client: ArmClient,
        intermediate_actions: list[str] | None = None,
        **kwargs,
    ) -> Observable:
        if intermediate_actions is None:
            intermediate_actions = []

        origin_site = (cont.current_device, cont.current_pos)
        target_site = (step.target_device.name, step.destination_pos)
        print(f"moving from {origin_site} to {target_site}")
        if not intermediate_actions:
            return sila_client.RobotController.MovePlate(origin_site, target_site)

        # with intermediate actions we need to use the standard sila labware transfer feature
        print(f"intermediate actions: {intermediate_actions}")

        class TransferHandler(ObservableProtocolHandler):
            def _protocol(self, client: ArmClient, **kwargs):
                pick_cmd = client.LabwareTransferManipulatorController.GetLabware(
                    HandoverPosition=(
                        cont.current_device,
                        cont.current_pos + 1,
                    ),  # counting start at 1 there
                    IntermediateActions=intermediate_actions,
                )
                finish_observable_command(pick_cmd)
                # PlacePlate is blocking and not observable
                client.RobotController.PlacePlate(target_site)

        observable = TransferHandler()
        # starts _protocol and handles the status
        observable.run_protocol(sila_client)
        return observable


class LabwareTransferHandler(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(step: MoveStep, cont: ContainerInfo, sila_client: ArmClient,
                         interactive_source: LabwareSite | None = None,
                         interactive_target: LabwareSite | None = None,
                         intermediate_actions: list[str] | None = None,
                         **kwargs) -> Observable:
        if intermediate_actions is None:
            intermediate_actions = []
        logging.debug(f"Creating LabwareTransferHandler for step {step.name}")
        logging.debug("interactive source: ", interactive_source)
        logging.debug("interactive target: ", interactive_target)
        logging.debug("intermediate actions: ", intermediate_actions)

        class TransferHandler(ObservableProtocolHandler):
            def _protocol(self, client: ArmClient, **_kwargs):
                # prepare source and mover
                handover = Site(cont.current_device, cont.current_pos + 1)  # the feature starts counting at 1
                mover_prepare = sila_client.LabwareTransferManipulatorController.PrepareForInput(
                    handover, 1, cont.labware_type, str(cont.barcode),
                )
                if interactive_source:
                    source_prepare = interactive_source.PrepareForOutput(
                        Site(cont.current_device, 1), cont.current_pos + 1,
                    )
                    finish_observable_command(source_prepare)
                    if not source_prepare.status == CommandExecutionStatus.finishedSuccessfully:
                        raise Exception(f"target device failed to prepare {handover} for output: {source_prepare.get_responses()}")
                finish_observable_command(mover_prepare)
                """# check it the robot is able to perform the intermediate actions
                for intermediate in intermediate_actions:
                    if intermediate not in sila_client.LabwareTransferManipulatorController.AvailableIntermediateActions.get():
                        logging.warning(f"The mover says that {intermediate} is no available intermediate action")"""
                # pick with intermediate actions
                pick_cmd = sila_client.LabwareTransferManipulatorController.GetLabware(
                    handover, intermediate_actions
                )
                finish_observable_command(pick_cmd)
                # notify source
                if interactive_source:
                    # this should not be blocking
                    Thread(target=interactive_source.LabwareRemoved, daemon=True, args=[handover]).start()
                # prepare mover and target
                handover = Site(step.target_device.name, step.destination_pos + 1)
                mover_prepare = sila_client.LabwareTransferManipulatorController.PrepareForOutput(
                    handover, 1,
                )
                logging.info(f"delivering {cont} to {step.destination_pos + 1} (already added +1 for the feature)")
                if interactive_target:
                    target_prepare = interactive_target.PrepareForInput(
                        handover, step.destination_pos + 1, # the feature starts counting at 1
                        cont.labware_type, str(cont.barcode),
                    )
                    finish_observable_command(target_prepare)
                    if not target_prepare.status == CommandExecutionStatus.finishedSuccessfully:
                        raise Exception(f"target device failed to prepare {handover} for input: {target_prepare.get_responses()}")
                finish_observable_command(mover_prepare)
                # place
                place_cmd = sila_client.LabwareTransferManipulatorController.PutLabware(
                    handover, intermediate_actions,
                )
                finish_observable_command(place_cmd)
                # notify target
                if interactive_target:
                    # this should not be blocking
                    Thread(target=interactive_target.LabwareDelivered, daemon=True, args=[handover]).start()

        observable = TransferHandler()
        # starts _protocol and handles the status
        observable.run_protocol(sila_client)
        return observable


