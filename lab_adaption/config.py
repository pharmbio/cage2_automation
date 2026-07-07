""" """

from lab_adaption.worker_adaption import Worker
from pathlib import Path


# optionally change it to your own implementation of
# laborchestrator.database_integration.status_db_interface.StatusDBInterface
from platform_status_db.larastatus.status_db_implementation import (
    StatusDBImplementation,
)

# change this to the module where you save your pythonLab processes
from lab_adaption import processes

# Comment out db_client to None to not use any database
db_client = StatusDBImplementation()

# comment out to use the default worker (i.e., just simulation)
worker_type = Worker

# lab_config to be sent to the scheduler
lab_config_file = str(
    Path(__file__).resolve().parent / "platform_config.yaml"
)

# controls the default time limit the orchestrator gives the scheduler for computing new schedules
# It can be changed via GUI at runtime
default_scheduling_time = 3  # seconds

# change to a solver name like CP-Solver or BottleneckPD which will be chosen on the scheduler.
scheduling_algorithm = "CP-Solver"

process_module = processes

# configures the initial view of the GUI.
arm_open = True  # View for genericroboticarm
db_open = True  # View for present labware in database
browser_open = True  # Sila-browser

# Gantt chart bar colors per device (device name -> color).
# Robot arm: red. Microscopes: shades of green (the two squids are close to
# each other). Liquid handlers: shades of blue.
device_colors = {
    "PFonRail": "#d62728",  # robot arm
    "Squid1": "#43a047",  # squid microscope (mid green)
    "Squid2": "#9ccc65",  # squid microscope (lime green, close-ish to Squid1)
    "MultiFlow": "#4fc3f7",  # liquid handler (dispenser) - light blue
    "Washer": "#1e88e5",  # 405TS washer (liquid handler) - mid blue
    "BlueWasher": "#002171",  # BlueWasher (liquid handler) - navy
    "Echo": "#e91e63",  # acoustic dispenser - pink
    "Cytomat1": "#ffb300",  # incubator - orange-yellow
    "Cytomat2": "#ffe082",  # incubator - light yellow
    "Sealer": "#9e9e9e",  # plate sealer - grey
}
