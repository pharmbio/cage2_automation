""" """

from .worker_adaption import Worker
from pathlib import Path


# optionally change it to your own implementation of
# laborchestrator.database_integration.status_db_interface.StatusDBInterface
from platform_status_db.larastatus.status_db_implementation import (
    StatusDBImplementation,
)

# change this to the module where you save your pythonLab processes
from . import processes

# Comment out db_client to None to not use any database
db_client = StatusDBImplementation()

# comment out to use the default worker (i.e., just simulation)
worker_type = Worker

# lab_config to be sent to the scheduler
lab_config_file = (
    Path(__file__).resolve().parent.parent / "lab_adaption" / "platform_config.yaml"
)

# controls the default time limit the orchestrator gives the scheduler for computing new schedules
# It can be changed via GUI at runtime
default_scheduling_time = 1  # seconds

# change to a solver name like CP-Solver or BottleneckPD which will be chosen on the scheduler.
scheduling_algorithm = "BottleneckPD"

process_module = processes
