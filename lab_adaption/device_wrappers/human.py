from laborchestrator.structures import ProcessStep, ContainerInfo
from .device_interface import DeviceInterface
try:
    from human_server.generated.client import Client as HumanClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as HumanClient
from sila2.client import ClientObservableCommandInstance
from sila2.framework import SilaAnyType


class HumanWrapper(DeviceInterface):
    def get_SiLA_handler(self, step: ProcessStep, cont: ContainerInfo, human_client: HumanClient, **kwargs) -> ClientObservableCommandInstance:
        if step.function == 'ask_for_ok':
            return human_client.HumanController.CustomCommand(
                Description="Say OK",
                ResponseStructure=SilaAnyType(type_xml="<DataType><Basic>Real</Basic></DataType>", value=1
            ))

        if step.function == 'do_task':
            return human_client.HumanController.CustomCommand(
                Description=kwargs['message'],
                ResponseStructure=SilaAnyType(type_xml="<DataType><Basic>Real</Basic></DataType>", value=1
            ))

        if step.function == 'request_number':
            return human_client.HumanController.CustomCommand(
                Description=kwargs["message"],
                ResponseStructure=SilaAnyType(type_xml="<DataType><Basic>Integer</Basic></DataType>", value=20
            ))

