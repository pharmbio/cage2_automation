# Installation
1. Download this package (alternatively fork the repository):
```bash
    git clone https://gitlab.com/OpenLabAutomation/adaption-template.git
    cd adaption-template
```
2. Use your favourite tool to create and activate a new python environment with Python 3.12 or higher. For example with pyvenv on linux:
```bash
   python -m venv labautomation
   source labautomation/bin/activate
```
3. Install all necessary packages:
   - to install all mandatory dependencies run:
```bash
    pip install -e .
```
   - to also install the example sila servers (necessary for the demo examples to run) add:
```bash
    pip install -r requirements_servers.txt
```
   - to also install requirements for stronger scheduling algorithms add:
```bash
    pip install -r requirements_mip_cp.txt
```
4. Install and set up the database

Installation: Run
```bash
    git clone https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git
    pip install -e platform_status_db/.
```
Setup: Run and follow the instructions to create an admin login to django. On windows you will have execute the steps manually.

```bash
    bash scripts/init_db.sh
```

Fill the database: Run
```bash
    python scripts/add_lab_setup_to_db.py
```
This adds the lab setup as described in platform_config.yml to the database.
Rerun this script after you customized the config file.

