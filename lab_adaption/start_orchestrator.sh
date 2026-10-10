#!/usr/bin/env bash

pip install git+https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git
pip install -r /opt/adaptation_template/requirements_servers.txt
pip install psycopg2-binary
# config.py imports lab_adaption, which is mounted but not installed in the image
export PYTHONPATH=/opt/adaptation_template/:$PYTHONPATH
laborchestrator -c /opt/adaptation_template/lab_adaption/config.py
