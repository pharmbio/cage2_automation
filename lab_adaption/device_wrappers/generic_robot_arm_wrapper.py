import logging
from collections import namedtuple
from threading import Thread
from weakref import WeakKeyDictionary

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


# Arms that can fetch a lid while the source device still prepares itself declare PrepareForInput
# as affected by the PlannedIntermediateActions metadata. SiLA then requires the metadata on every
# such call, so it is sent even when there is nothing to announce. Arms that cannot do this declare
# nothing, and sending it anyway would only earn a "received unexpected metadata" warning, so it is
# left out there. Whether an arm expects it is asked once per client, not per transfer.
_announcement_expected_by_client: WeakKeyDictionary[object, bool] = WeakKeyDictionary()

# The metadata value is a structure wrapping the list, because SiLA metadata cannot be a plain
# list. sila2 identifies a structure value by its field names, so a namedtuple defined here is
# accepted just like the one the client builds from the feature definition. Do not pass a dict
# instead: a single-field structure takes the dict as the field value, and serialising it yields
# the dict's keys rather than its values, without any error.
PlannedIntermediateActions = namedtuple("PlannedIntermediateActions_Struct", ["IntermediateActions"])


def expects_action_announcement(sila_client: ArmClient) -> bool:
    """
    Whether this arm declares PrepareForInput as affected by the PlannedIntermediateActions
    metadata, i.e. whether that metadata has to be sent with every PrepareForInput call.
    :param sila_client:
    :return:
    """
    expected = _announcement_expected_by_client.get(sila_client)
    if expected is not None:
        return expected
    planning = getattr(sila_client, "IntermediateActionPlanning", None)
    transfer = sila_client.LabwareTransferManipulatorController
    if planning is None:
        # an arm that does not know the feature at all, e.g. one running an older server
        expected = False
    else:
        affected = planning.PlannedIntermediateActions.get_affected_calls()
        # the server may declare the whole feature instead of the single command
        expected = bool({transfer["PrepareForInput"].fully_qualified_identifier,
                         transfer.fully_qualified_identifier}.intersection(affected))
    _announcement_expected_by_client[sila_client] = expected
    return expected


def announcement_metadata(sila_client: ArmClient, intermediate_actions: list[str]) -> dict:
    """
    The metadata announcing the intermediate actions of the GetLabware following a PrepareForInput,
    as keyword arguments for that call. Empty for arms that do not expect an announcement.
    The announcement is non-binding: the actions are passed to GetLabware as usual either way.
    :param sila_client:
    :param intermediate_actions: the actions the following GetLabware will be given
    :return:
    """
    if not expects_action_announcement(sila_client):
        return {}
    planned = sila_client.IntermediateActionPlanning.PlannedIntermediateActions
    return {"metadata": [planned(PlannedIntermediateActions(IntermediateActions=intermediate_actions))]}


class GenericRobotArmWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: MoveStep,
        labware: list[ContainerInfo],
        sila_client: ArmClient,
        intermediate_actions: list[str] | None = None,
        **kwargs,
    ) -> Observable:
        if intermediate_actions is None:
            intermediate_actions = []
        if len(labware) != 1:
            logging.warning(f"GenericRobotArmWrapper can only handle one container at a time. Given labware: {labware}")
        cont = labware[0]
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


def announce_intermediate_actions(sila_client: ArmClient, intermediate_actions: list[str]) -> dict:
    """
    Builds the metadata that announces the intermediate actions to PrepareForInput, so that the arm
    can already do its share of them (fetching a lid) while the source device prepares itself.
    Arms that can prepare intermediate actions require the announcement with every PrepareForInput,
    so an empty list is announced as well. Arms without the IntermediateActionPlanning feature get
    no metadata and do the intermediate actions during GetLabware as before.
    :param sila_client:
    :param intermediate_actions: the actions the following GetLabware will be given
    :return: keyword arguments to pass to PrepareForInput
    """
    planning = getattr(sila_client, "IntermediateActionPlanning", None)
    if planning is None:
        return {}
    return {"metadata": [planning.PlannedIntermediateActions(intermediate_actions)]}


class LabwareTransferHandler(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(step: MoveStep, labware: list[ContainerInfo], sila_client: ArmClient,
                         interactive_source: LabwareSite | None = None,
                         interactive_target: LabwareSite | None = None,
                         intermediate_actions: list[str] | None = None,
                         **kwargs) -> Observable:
        if intermediate_actions is None:
            intermediate_actions = []
        main_labware = labware[0]
        logging.debug(f"Creating LabwareTransferHandler for step {step.name}")
        logging.debug("interactive source: ", interactive_source)
        logging.debug("interactive target: ", interactive_target)
        logging.debug("intermediate actions: ", intermediate_actions)

        class TransferHandler(ObservableProtocolHandler):
            def _protocol(self, client: ArmClient, **_kwargs):
                # prepare source and mover
                handover = Site(main_labware.current_device, main_labware.current_pos + 1)  # the feature starts counting at 1
                # arms that prepare intermediate actions require the announcement on every
                # PrepareForInput. Nothing is announced yet: passing intermediate_actions here
                # instead would let the arm fetch the lid already while the source device
                # prepares itself, but that list is also the one given to PutLabware, so it has
                # to be split into a get and a put part first.
                mover_prepare = sila_client.LabwareTransferManipulatorController.PrepareForInput(
                    handover, 1, main_labware.labware_type, str(main_labware.barcode),
                    **announcement_metadata(sila_client, []),
                )
                if interactive_source:
                    source_prepare = interactive_source.PrepareForOutput(
                        Site(main_labware.current_device, 1), main_labware.current_pos + 1,
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
                logging.info(f"delivering {main_labware} to {step.destination_pos + 1} (already added +1 for the feature)")
                if interactive_target:
                    target_prepare = interactive_target.PrepareForInput(
                        handover, step.destination_pos + 1, # the feature starts counting at 1
                        main_labware.labware_type, str(main_labware.barcode),
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
