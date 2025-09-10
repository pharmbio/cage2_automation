from pythonlab.resource import ServiceResource, LabwareResource
try:
    from pandas import DataFrame
except ModuleNotFoundError:
    from typing import Any as DataFrame
from echo_server.communication.parsing_utilities import rectangle_to_survey


class EchoServiceResource(ServiceResource):
    """
    Implementation of an Echo550 for pythonLab
    """
    def execute_transfer_protocol(self, source_plate: LabwareResource, target_plate: LabwareResource,
                                  protocol: str | DataFrame, **kwargs):
        if isinstance(protocol, str):
            if "duration" not in kwargs:
                kwargs["duration"] = 120
            kwargs["fct"] = "execute_protocol"
            kwargs["protocol"] = protocol
        elif isinstance(protocol, DataFrame):
            if "duration" not in kwargs:
                kwargs["duration"] = len(protocol)
            kwargs["fct"] = "custom_protocol"
            kwargs["transfers"] = protocol

        self.proc.add_process_step(self, [source_plate, target_plate], **kwargs)

    def survey_for_protocol(self, source_plate: LabwareResource, protocol: str | DataFrame, **kwargs):
        if isinstance(protocol, str):
            if "duration" not in kwargs:
                kwargs["duration"] = 70
            kwargs["fct"] = "survey"
            kwargs["protocol"] = protocol
        elif isinstance(protocol, DataFrame):
            kwargs["fct"] = "custom_survey"
            start_row, start_col, num_rows, num_cols = rectangle_to_survey(protocol)
            kwargs.update({
                "start_row": start_row,
                "start_col": start_col,
                "num_rows": num_rows,
                "num_cols": num_cols,
            })
            kwargs["duration"] = num_rows * num_cols
        self.proc.add_process_step(self, [source_plate], **kwargs)
