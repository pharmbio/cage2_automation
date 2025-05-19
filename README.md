# Lab Automation Framework Template and Demo
This package serves as an installable template to adapt the automation framework consisting of
[LabScheduler](https://gitlab.com/opensourcelab/pythonlabscheduler),
[Laborchestrator](https://gitlab.com/opensourcelab/laborchestrator),
[PythonLab](https://gitlab.com/opensourcelab/pythonLab),
[PlatformStatusDataBase](https://gitlab.com/StefanMa/platform_status_db)
and some SiLA-Servers to a new robotic lab.
It also contains out of the box running demo examples.

## Target Audience
People who have a robotic arm with several devices they can access via SiLA (or at least python) and look for a
framework do describe, orchestrate and schedule workflows on these devices. Some programming skills are necessary.

## Content
- Install scripts to install necessary software packages (database, scheduler, pythonLab, orchestrator)
- Template for custom robotic lab setup and interface for customizable funtionalities

## Installation
1. Download this package:
```bash
    git clone https://gitlab.com/opensourcelab/openlab-site/lab-automation.git
    cd lab-automation
    git checkout release/0.1.0
```
2. Use your favourite tool to create and activate a new python environment with python 3.11 or higher. For example with pyvenv on linux:
```bash
   python -m venv labautomation
   source labautomation/bin/activate
```
3. Install all necessary packages:
   - to install all mandatory dependencies run:
```bash
    pip install -r requirements.txt -e .
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
    git clone https://gitlab.com/StefanMa/platform_status_db.git
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

## Startup
Call from different console tabs
- to start the scheduler:
```bash
    labscheduler --insecure -p 50066
```
- to start the django database view (optional). If you changed directory, adapt the path:
```bash
    python platform_status_db/platform_status_db/manage.py runserver
```
- to start the orchestrator:
```bash
    laborchestrator
```
- to start demo servers:
```bash
    start_sila_servers
```

## Usage
You can access the GUI for different components:
- database of present labware at [http://127.0.0.1:8000/job_logs/present_labware/](http://127.0.0.1:8000/job_logs/present_labware/)
- orchestrator at [http://127.0.0.1:8050/](http://127.0.0.1:8050/)
- the human interaction sila server: [http://127.0.0.1:8054/](http://127.0.0.1:8054/)
- view and manual control of the robotic arm: [http://127.0.0.1:8055/](http://127.0.0.1:8055/)

To see how the example servers are controlled from the orchestrator, go to the the orchestrator GUI and load and start one of the
example processes. For a detailed explanation on the GUI usage see our [Demo Guide](docs/quickstart.md)
- GreeterTest: Sends a Hello-World to the sila2-example-server
- MoverTest: You can view the robots movements in the roboter GUI
- HumanTest: you will have to finish the tasks in the human interaction GUI
- InterestingExample: A more complex workflow with runtime decisions based on human interaction



## Support
For support, feel free to contact stefanmaak@freenet.de

## Authors and acknowledgment
Maintained by Stefan Maak(Uppsala University) and Mark Dörr of the working group of Prof. Bornscheuer in Uni Greifswald.

## License
MIT Licence.

## Project status
The project combines packages with version control and unit-tests.
It therefore is and should stay installable and usable, but is (probably) not totally free of bugs.
It is also under active development.
