from abc import ABC

from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.human import HumanServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
from pythonlab.resources.services.washer_dispenser import WasherDispenserServiceResource
from pythonlab.resources.services.incubation import IncubatorServiceResource
from pythonlab.resources.services.microscope import MicroscopeServiceResource
from pythonlab.resources.services.sealer import PlateSealerServiceResource
from pythonlab.resource import LabwareResource
from pythonlab.process import PLProcess
from .pythonlab_extensions.echo_service_resource import EchoServiceResource

class BasicProcess(PLProcess, ABC):
    def __init__(
        self, process_name: str, num_plates: int = 0, priority=7
    ):  # 0 has highest priority
        self.num_mw_plates = num_plates
        self.name = process_name

        super().__init__(priority=priority)

    def create_resources(self):
        # the device names should match the ones in the platform_config
        self.hotel1 = LabwareStorageResource(proc=self, name="Hotel1")
        self.hotel2 = LabwareStorageResource(proc=self, name="Hotel2")
        self.fridge = LabwareStorageResource(proc=self, name="Fridge")
        self.robot_arm = MoverServiceResource(proc=self, name="PFonRail")
        self.washer = WasherDispenserServiceResource(proc=self, name="BlueWasher")
        self.dispenser = WasherDispenserServiceResource(proc=self, name="MultiFlow")
        self.incubator1 = IncubatorServiceResource(proc=self, name="Cytomat1")
        self.incubator2 = IncubatorServiceResource(proc=self, name="Cytomat2")
        self.squid1 = MicroscopeServiceResource(proc=self, name="Squid1")
        self.sealer = PlateSealerServiceResource(proc=self, name="Sealer")
        self.echo = EchoServiceResource(proc=self, name="Echo")
        self.human = HumanServiceResource(proc=self, name="Human")

        # the continers are automatically named/enumerated. You can change the naming without causing problems
        self.containers = [
            LabwareResource(
                proc=self, name=f"{self.name}_cont_{cont}", lidded=True, filled=False
            )
            for cont in range(self.num_mw_plates)
        ]

    def process(self):
        raise NotImplementedError
