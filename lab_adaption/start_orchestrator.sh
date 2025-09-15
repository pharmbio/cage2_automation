#!/usr/bin/env bash

pip install git+https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git
pip install -r /opt/adaptation_template/requirements_servers.txt
pip install psycopg2-binary
python -m lab_adaption.start_script
