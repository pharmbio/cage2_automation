import logging
from typing import Union, Optional, List
from asyncio import gather, sleep
import time

from laborchestrator.engine.worker_interface import Observable, ObservableProtocolHandler
from laborchestrator.structures import ContainerInfo, MoveStep
from sila2.client import ClientObservableCommandInstance
from sila2.framework import CommandExecutionStatus

from .labware_site import LabwareSite, LabwareManipulator, Site
from . import DeviceInterface, finish_observable_command
from uppsala_cell_lab.devices import DeviceInterface


async def finish(cmd: ClientObservableCommandInstance):
    """
    Waits until the command finishes
    :param cmd:
    :return:
    """
    while not cmd.done:
        await sleep(.1)

def finish_sync(cmds: List[ClientObservableCommandInstance]):
    while not all(cmd.done for cmd in cmds):
        time.sleep(.01)

class GenericRobotArmWrapper(DeviceInterface):
    def get_SiLA_handler(self, step: MoveStep, cont: ContainerInfo,
                         labware_manipulator: LabwareManipulator,
                         interactive_source: Optional[LabwareSite] = None,
                         interactive_target: Optional[LabwareSite] = None,
                         intermediate_actions_get: list[str] | None = None,
                         intermediate_actions_put: list[str] | None = None,
                         ) -> Observable:
        if intermediate_actions_get is None:
            intermediate_actions_get = []
        if intermediate_actions_put is None:
            intermediate_actions_put = []
        # because stupid people decided to start counting at 1.....:
        origin_site = Site(cont.current_device, cont.current_pos + 1)
        target_site = Site(step.target_device.name, step.destination_pos + 1)
        print(f"moving from {origin_site} to {target_site} (already added 1 to indices)")
        print(f"intermediate actions: in get: {intermediate_actions_get} in put: {intermediate_actions_put}")
        class TransferHandler(ObservableProtocolHandler):
            async def _protocol(self, *args, **kwargs):
                # prepare origin device for output and mover for input
                print("preparing picking")
                success = await self.prepare_pick(origin_site)
                if not success:
                    logging.error("Pick preparations gone wrong")
                print("preparations for picking done")
                # pick the labware
                cmd_info = labware_manipulator.GetLabware(
                    HandoverPosition=origin_site,
                    IntermediateActions=intermediate_actions_get,
                )
                await finish(cmd_info)
                if not cmd_info.status == CommandExecutionStatus.finishedSuccessfully:
                    logging.error("Picking went wrong")
                # inform the origin device
                if interactive_source:
                    interactive_source.LabwareRemoved(origin_site)
                # prepare target device for input and mover for output
                print("prepare placing")
                success = await self.prepare_place(target_site)
                if not success:
                    logging.error("Place preparations gone wrong")
                print("preparations for placing done")
                # place the labware
                cmd_info = labware_manipulator.PutLabware(
                    HandoverPosition=target_site,
                    IntermediateActions=intermediate_actions_put,
                )
                await finish(cmd_info)
                if not cmd_info.status == CommandExecutionStatus.finishedSuccessfully:
                    logging.error("Placing went wrong")
                # inform the target device
                if interactive_target:
                    interactive_target.LabwareDelivered(target_site)

            @staticmethod
            async def prepare_pick(site: Site) -> bool:
                commands = [labware_manipulator.PrepareForInput(
                    HandoverPosition=site,
                    InternalPosition=1,
                    LabwareType="",
                    LabwareUniqueID="",
                )]
                if interactive_source:
                    commands.append(interactive_source.PrepareForOutput(
                        HandoverPosition=Site(site.device, 1),
                        InternalPosition=site.position_index,
                    ))
                await gather(*[finish(cmd) for cmd in commands])
                return all(cmd.status == CommandExecutionStatus.finishedSuccessfully for cmd in commands)

            @staticmethod
            async def prepare_place(site: Site) -> bool:
                commands = [labware_manipulator.PrepareForOutput(
                    HandoverPosition=site,
                    InternalPosition=1,
                )]
                if interactive_target:
                    commands.append(interactive_target.PrepareForInput(
                        HandoverPosition=Site(site.device, 1),
                        InternalPosition=site.position_index,
                        LabwareType="",
                        LabwareUniqueID="",
                    ))
                await gather(*[finish(cmd) for cmd in commands])
                return all(cmd.status == CommandExecutionStatus.finishedSuccessfully for cmd in commands)

        observable = TransferHandler()
        observable.run_protocol(labware_manipulator)
        return observable

    def get_next_free_position(self, client) -> Union[int, None]:
        logging.error("What kind of a question is this to am arm???")
        return 0
