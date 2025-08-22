import logging
from laborchestrator.engine.worker_interface import (
    Observable,
)
from laborchestrator.structures import ContainerInfo, ProcessStep

from . import DeviceInterface
import pandas as pd

try:
    from echo_server import Client as EchoClient
except ModuleNotFoundError:
    from sila2.client import SilaClient as EchoClient

    logging.warning("Ech server seems to be not installed")


class EchoWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: EchoClient,
        **kwargs,
    ) -> Observable:
        # transfers defined by a csv file
        if step.function == "execute_protocol":
            protocol = step.data.get("protocol", "")
            if not protocol:
                logging.warning(f"Protocol for step {step.name} not specified")
            logging.debug(f"Executing {protocol} on Echo")
            return sila_client.EchoProtocolController.ExecuteProtocol(
                ProtocolName = protocol,
            )
        elif step.function == "survey":
            protocol = step.data.get("protocol", "")
            if not protocol:
                logging.warning(f"Protocol for survey {step.name} not specified")
            logging.debug(f"Executing survey for {protocol} on Echo")
            return sila_client.EchoProtocolController.DoSurveyForProtocol(
                ProtocolName = protocol,
            )
        elif step.function == "custom_survey":
            start_row = step.data.get("start_row", 0)
            start_col = step.data.get("start_col", 0)
            num_rows = step.data.get("num_rows", 16)
            num_cols = step.data.get("num_cols", 24)
            logging.debug(f"Executing survey starting at {(start_row, start_col)}"
                          f" of size {(num_rows, num_cols)}on Echo")
            return sila_client.EchoProtocolController.DoCustomSurvey(
                StartRow=start_row, StartCol=start_col, NumRows=num_rows, NumCols=num_cols,
            )
        # transfers defined by a pandas dataframe
        elif step.function == "custom_protocol":
            df = step.data.get("transfers", None)
            if isinstance(df, pd.DataFrame):
                # Make columns lowercase once
                df.columns = df.columns.str.lower()
                # Now zip them case-insensitively
                transfer_list = list(zip(df["source well"], df["destination well"], df["transfer volume"].astype(float)
                ))
            else:
                logging.error("define 'transfers' in kwargs as pandas dataframe.")
            return sila_client.EchoProtocolController.DoWellTransfer(transfer_list)
