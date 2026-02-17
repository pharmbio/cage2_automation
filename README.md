# Lab Automation Framework Template and Demo
This package serves as an installable template to adapt the automation framework consisting of
[LabScheduler](https://gitlab.com/OpenLabAutomation/lab-automation-packages/lab-scheduler),
[Laborchestrator](https://gitlab.com/OpenLabAutomation/lab-automation-packages/laborchestrator),
[PythonLab](https://gitlab.com/OpenLabAutomation/lab-automation-packages/pythonLab),
[PlatformStatusDataBase](https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db)
and some SiLA-Servers to a new robotic lab.
It also contains out of the box running demo examples.

## Target Audience
People who have a robotic arm with several devices they can access via SiLA (or at least python) and look for a
framework do describe, orchestrate and schedule workflows on these devices. Some programming skills are necessary.
### Some examples for adaption of the template:
<table>
    <td align="center">
      <img src="https://gitlab.com/OpenLabAutomation/data/-/raw/main/adaptions/lara_robot_platform_full_view.JPG" width="250"><br>
      <sub>
      <a href="https://gitlab.com/lara-uni-greifswald/lara-processes/-/tree/develop?ref_type=heads">
      <b>LARA Platform Greifswald</b>
      </a></sub>
    </td>
    <td align="center">
      <img src="https://gitlab.com/OpenLabAutomation/data/-/raw/main/adaptions/uppsala_cage2.jpg" width="250"><br>
      <sub>
      <a href="https://github.com/pharmbio/cage2_automation">
      <b>Uppsala – Cage2 (in build-up)</b>
      </a></sub>
    </td>
    <td align="center">
      <img src="https://gitlab.com/OpenLabAutomation/data/-/raw/main/adaptions/uppsala_imaging_room.jpg" width="250"><br>
      <sub>
      <a href="https://gitlab.com/StefanMa/imager-automation">
      <b>Uppsala – Imaging Room</b>
      </a></sub>
    </td>
    <td align="center">
      <img src="https://gitlab.com/OpenLabAutomation/data/-/raw/main/adaptions/demo_lab.jpg" width="250"><br>
      <sub>
        <a href="https://gitlab.com/OpenLabAutomation/demo-lab">
          <b>Demo Lab</b>
        </a></sub>
    </td>
  </tr>
</table>


## Content
- Install scripts to install necessary software packages (database, scheduler, pythonLab, orchestrator)
- Template for custom robotic lab setup and interface for customizable funtionalities

## Installation
1. Download this package (alternatively fork the repository):
```bash
    git clone https://gitlab.com/OpenLabAutomation/adaption-template.git
    cd lab-automation
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

## Startup
Call from different console tabs

**Option 1:** In gnome terminal you could start all four o the following services in different tabs by running

   ```bash
       bash scripts/run_services.sh
   ```

**Option 2:** Otherwise use individual commands (remember activating the virtual environment):

   - to start the scheduler:
   ```bash
       labscheduler
   ```
   - to start the django database view (optional). If you changed directory, adapt the path:
   ```bash
       run_db_server
   ```
   - to start the orchestrator:
   ```bash
       laborchestrator
   ```
   - to start demo servers:
   ```bash
       start_sila_servers
   ```

## Docker compose
Alternatively you can use docker compose to start all services. Make sure you have docker and docker-compose installed.
Then run
```bash
   docker-compose up --build
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

## Trouble shooting
Future versions of used packages might contain breaking changes. This is the output of `pip list` in a freshly installed working virtual environment:

<details>
<summary>Show full output of pip list</summary>

```text
Package                   Version     Editable project location
------------------------- ----------- -----------------------------------------------------
absl-py                   2.3.1
annotated-types           0.7.0
asgiref                   3.9.1
blinker                   1.9.0
cachelib                  0.13.0
certifi                   2025.8.3
charset-normalizer        3.4.3
click                     8.2.1
dash                      3.0.4
dash-bootstrap-components 2.0.4
dash-extensions           2.0.4
dash_interactive_graphviz 0.3.0
dataclass-wizard          0.35.1
Django                    5.2.6
EditorConfig              0.17.1
Flask                     3.0.3
Flask-Caching             2.3.1
genericroboticarm         1.3.3
graphviz                  0.21
grpcio                    1.71.0
grpcio-tools              1.71.0
human_server              1.1.6
idna                      3.10
ifaddr                    0.2.0
immutabledict             4.2.1
importlib_metadata        8.7.0
itsdangerous              2.2.0
Jinja2                    3.1.6
jsbeautifier              1.15.4
lab_adaption              0.1.0       /home/stefan/tmp/adaption-template
laborchestrator           0.2.7
labscheduler              0.2.47
lxml                      6.0.1
markdown-it-py            4.0.0
MarkupSafe                3.0.2
mdurl                     0.1.2
more-itertools            10.8.0
narwhals                  2.3.0
nest-asyncio              1.6.0
networkx                  3.5
numpy                     2.3.2
ortools                   9.9.3963
packaging                 25.0
pandas                    2.3.2
pillow                    11.3.0
pip                       24.0
platform_status_db        0.2.0       /home/stefan/tmp/adaption-template/platform_status_db
plotly                    6.3.0
protobuf                  5.29.4
pydantic                  2.11.7
pydantic_core             2.33.2
Pygments                  2.19.2
PySCIPOpt                 5.6.0
pyserial                  3.5
python-dateutil           2.9.0.post0
pythonlab                 0.2.2
pytz                      2025.2
PyYAML                    6.0.2
requests                  2.32.5
retrying                  1.4.2
rich                      14.1.0
setuptools                80.9.0
shellingham               1.5.4
sila2                     0.12.2
sila2_example_server      0.0.0
simplejson                3.20.1
six                       1.17.0
sqlparse                  0.5.3
typer                     0.17.3
typing_extensions         4.15.0
typing-inspection         0.4.1
tzdata                    2025.2
urllib3                   2.5.0
Werkzeug                  3.0.6
zeroconf                  0.147.0
zipp                      3.23.0

```

</details>


## Support
For support, feel free to contact stefanmaak@freenet.de

## Authors and acknowledgment
Maintained by Stefan Maak(Uppsala University).

Contributors:

- Mark Dörr of the working group of Prof. Bornscheuer in Uni Greifswald
- Djura Smith of durch escience center

## License
MIT Licence.

## Project status
The project combines packages with version control and unit-tests.
It therefore is and should stay installable and usable, but is (probably) not totally free of bugs.
It is also under active development.
