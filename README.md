# Lab Automation



## LabOrchestrator environment guide

## Description
This package only consist of an installation script for several packages
in [opensoucelab](https://gitlab.com/opensourcelab/) which are intended to work
together with the [laborchestrator](https://gitlab.com/opensourcelab/laborchestrator) and documentation for how to use them. 
These packages contain a [scheduler](https://gitlab.com/opensourcelab/pythonlabscheduler),
a supporting [database](https://gitlab.com/StefanMa/platform_status_db),
some (LARA-specialized) [utility tools](https://gitlab.com/StefanMa/lara-tools) for starting sila servers, creating simulations and visualization,
a process description language named [PythonLab](https://gitlab.com/opensourcelab/pythonLab),
a collection of [SiLA-servers](https://gitlab.com/opensourcelab/devices) for certain lab devices (including simulations)
and finally a [specialization](https://gitlab.com/lara-uni-greifswald/lara-processes) of the laborchestrator for the Greifswald robot platform LARA

## Badges
On some READMEs, you may see small images that convey metadata, such as whether all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
To install all packages, simply run 

`python3.8 full_install_script.py`

This will guide you through the packages and ask which one to install.

Afterwards (in case, you installed the platform_status_db), you should run 

`python3.8 full_install_script.py --init` 

to initialize the django database and create admin credentials.

With 

`python3.8 full_install_script.py --test`

you can run the automatic pytest tests for most packages (Do not worry, when the mip_solver test of the scheduler fails).

At any point in time, you can update your installation with 

`python3.8 full_install_script.py --update`

# Quickstart Guide

The orchestrator can work without PythonLab and the database,
but to understand the software, it's recommended to use the greifswald-specialization, which uses both.

### Remark:
    The steps 1, 3, 5, 6 and 8 can done by simply executing the
    `open_tabs.sh` or `open_tabs.bat` script depending on your OS.
    We still recommend to do them step by step the first time to understand,
    whats happening.

1. #### Starting the orchestrator GUI:

    Go into `lara_implementation/lara_processes` and type
    
    `python3.8 start_script.py`
    
    This will start a dash-app running on [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

2. #### Load a process
    
    You should be able to find some options in the first dropdown menu. These are all suitable process files found in
    `orchestrator/tests/test_data/`. Choose any process and add it to the orchestrator by clicking "Add Process". In the free area below,
    there should appear a graph representing the workflow of the chosen process.
    For a first test, we recommend the IncReadProcess.
    ![Screenshot of loaded GreetingExampleProcess-workflow](/images/workflow.png "Workflow")

3. #### Start the scheduler
    
    (If installed) the scheduler can be started as a SiLA-Server by running
    
    `python3.8 -m scheduler_server --insecure -p 50068` 
    
    The choice of port is not important as long as is does not block the device servers (currently 50051 - 50061) 

4. #### Schedule your process
    
    By chosing the added process in the second dropdown menu in the orchestrator GUI and clicking "Schedule Process", you mark the process as to be scheduled. The orchestrator will automatically discover the scheduler and use it to get a schedule. This will be visible as gantt chart in the upper part of the GUI.
    
    ![Screenshot of scheduled workflow](/images/schedule.png "Schedule")

5. #### Start the database web interface
    Go into `platform_status_database/platform_status_db` and type
    
    `python3.8 manage.py runserver`

    This starts the django webinterface for your database. You can visit the admin interface
    at [http://127.0.0.1:8000/admin/job_logs/](http://127.0.0.1:8000/admin/job_logs/) (use the credentials you set up during installation)
    and the user interface at [http://127.0.0.1:8000/job_logs/](http://127.0.0.1:8000/job_logs/)
    The user interface is not yet developed a lot. The admin-view comes with django.
    You can see its documentation at [https://docs.djangoproject.com/en/4.1/intro/tutorial02/](https://docs.djangoproject.com/en/4.1/intro/tutorial02/)

6. #### Start the ServerManager
    
    Go into `lara_server_tools/lara_simulation/lara_simulation` and type
    `python3.8 dash_app.py` 

    That starts a dash webinterface where you can start and stop your device SiLA2 servers.

7. #### Start some Servers
    You can visit the ServerManager webinterface at [http://127.0.0.1:8051/](http://127.0.0.1:8051/).
    Tick the boxes of all devices, you want to start/stop servers for and press start/stop.
    Do not tick `secure`.
    To simulate for example running the IncReadProcess, you will need 

    - Fanuc F5 Robotic Arm
    - Plate Storage Carousel
    - Thermo Cytomat2 (C1)
    - Thermo VarioskanLUX (lower)
    - Omron MS3 BarcodeReade

8. #### Start the Visualization (optional)
    
    Go into `lara_server_tools/lara_simulation/lara_simulation` and type
    `python3.8 visualize_from_json.py`.
    
    The ServerManager produces text files showing the devices in ASCII art.
    These get updated frequently and are monitored using the curses python module.
    If you started some servers with the ServerManager, you should see some devices.
    You can stop the script any time with Ctrl+C.

9. ### Start the Process

    Go back to the orchestrator GUI at [http://127.0.0.1:8050/](http://127.0.0.1:8050/)
    , choose the process in the second Dropdown menu and press _Start Process_.

10. ### Enjoy the simulation
    
    If everything went according to plan, you should see the current time bar moving through
    the gantt chart, the workflow-bubbles turning green after step completions and the visualization change.
    The simulated devices are much faster than the real ones, so the schedule will change accordingly.

Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
For support, feel free to contact maaks@uni-greifswald.de. 

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Maintained by Stefan Maak and Mark Dörr of the workinggroup of Prof. Bornscheuer in Uni Greifswald.

## License
MIT Licence.

## Project status
The project is still in an experimental state, but improves continuously.
We have unit tests and use the software is used to run experiments, 
but there are still lots of changes happening and bugs being discovered. 
