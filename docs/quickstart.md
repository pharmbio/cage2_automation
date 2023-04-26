## Quickstart Guide

This guide explains how to start the different components of the automation framework and give a simple example on their usage.

### Starting the components

There are scripts `open_tabs.sh` and `open_tabs.bat` for linux and windows respectively
to execute all the following steps.
We still recommend to do them step by step the first time to understand,
what is happening.

**Note:** The scripts might not work if f.e. gnome-terminal is not installed on linux.
Just follow the manual steps, then.

1. #### Starting the orchestrator GUI:
    Go into `lara_implementation/lara_processes` and type
    
    `python start_script.py`
    
    This will start a dash-app running on [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

2. #### Start the scheduler
    
    (If installed) the scheduler can be started as a SiLA-Server by running
    
    `python -m scheduler_server --insecure -p 50068` 
    
    The choice of port is not important as long as is does not block the device servers (currently 50051 - 50061) 

3. #### Start the database web interface
    Go into `platform_status_database/platform_status_db` and type
    
    `python manage.py runserver`

    This starts the django webinterface for your database. You can visit the admin interface
    at [http://127.0.0.1:8000/admin/job_logs/](http://127.0.0.1:8000/admin/job_logs/) (use the credentials you set up during installation)
    and the user interface at [http://127.0.0.1:8000/job_logs/](http://127.0.0.1:8000/job_logs/).

    The user interface is not yet developed a lot. The admin-view comes with django.
    You can see its documentation at [https://docs.djangoproject.com/en/4.1/intro/tutorial02/](https://docs.djangoproject.com/en/4.1/intro/tutorial02/)

4. #### Start the ServerManager
    
    Go into `lara_server_tools/lara_simulation/lara_simulation` and type
    `python dash_app.py` 

    That starts a dash webinterface where you can start and stop your device SiLA2 servers.

5. #### Start the Visualization (optional)
    
    Go into `lara_server_tools/lara_simulation/lara_simulation` and type
    `python start_visualization.py`.
    
    The ServerManager produces text files showing the devices in ASCII art.
    These get updated frequently and are monitored using the curses python module.
    If you started some servers with the ServerManager, you should see some devices.
    You can stop the script any time with Ctrl+C.

### Running a process simulation


1. #### Load a process
    Go to [http://127.0.0.1:8050/](http://127.0.0.1:8050/).

    You should be able to find some options in the first dropdown menu. These are all suitable process files found in
    `orchestrator/tests/test_data/`. Choose any process and add it to the orchestrator by clicking "Add Process". In the free area below,
    there should appear a graph representing the workflow of the chosen process.
    For a first test, we recommend the IncReadProcess.
    ![Screenshot of loaded GreetingExampleProcess-workflow](/images/workflow.png "Workflow")

2. #### Schedule your process
    
    By choosing the added process in the second dropdown menu in the orchestrator GUI and clicking "Schedule Process", you mark the process as to be scheduled. The orchestrator will automatically discover the scheduler and use it to get a schedule. This will be visible as gantt chart in the upper part of the GUI.
    
    ![Screenshot of scheduled workflow](/images/schedule.png "Schedule")

3. #### Start some Servers
    You can visit the ServerManager webinterface at [http://127.0.0.1:8051/](http://127.0.0.1:8051/).
    Tick the boxes of all devices, you want to start/stop servers for and press start/stop.
    Do not tick `secure`.
    To simulate for example running the IncReadProcess, you will need 

    - Fanuc F5 Robotic Arm
    - Plate Storage Carousel
    - Thermo Cytomat2 (C1)
    - Thermo VarioskanLUX (upper)
    - Omron MS3 BarcodeReade
    
    After a server is marked running, you should be able to see its ASCII-visualization in your visualization

4. ### Ensure Labware presence
    To run the process with database support we have to create database entries for all labware involved in the process.
    This can bo done by choosing the process in the second dropdown-menu and pressing __Add Containers to DB__.
    Afterward, you should find all the labware on [http://127.0.0.1:8000/job_logs/present_labware/](http://127.0.0.1:8000/job_logs/present_labware/)
    Additionally, our devices need to be filled correctly. For this simulation, 
    you can go to [http://127.0.0.1:8051/](http://127.0.0.1:8051/), select devices and 
    consecutively press __Reset Simulation__ and __Restart Servers__. If you do this with the Carousel,
    you will notice in the visualization, how its first columns is filled.

5. ### Start the Process

    Go back to the orchestrator GUI at [http://127.0.0.1:8050/](http://127.0.0.1:8050/)
    , choose the process in the second Dropdown menu and press _Start Process_.

6. ### Enjoy the simulation
    
    If everything went according to plan, you should see the current time bar moving through
    the gantt chart, the workflow-bubbles turning green after step completions and the visualization change.
    The simulated devices are much faster than the real ones, so the schedule will change accordingly.
    ![Screenshot partially run process](/images/running.png "Running Process")
    [http://127.0.0.1:8000/job_logs/present_labware/](http://127.0.0.1:8000/job_logs/present_labware/) will also change accordingly if you refresh the page.
