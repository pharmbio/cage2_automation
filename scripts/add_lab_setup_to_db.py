"""
Use this script to populate the database with devices and positions according to the lab_config file.
It does not check whether devices already exists. So, running this multiple times results in duplicate database entries.
You can remove all present devices and positions running the wipe_lab command.
"""

from platform_status_db.larastatus.status_db_implementation import (
    StatusDBImplementation,
)
from pathlib import Path

# change this if necessary
lab_config_file = (
    Path(__file__).resolve().parent.parent / "lab_adaption" / "platform_config.yaml"
)
# creates a client got the database
db_client = StatusDBImplementation()
# clear the database, if necessary
db_client.wipe_lab()

print("Populating the database with config from:", lab_config_file)
# populates the database
db_client.create_lab_from_config(lab_config_file.as_posix())
