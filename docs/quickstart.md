# Quickstart Guide

This guide lists the steps to load and run a process assuming you already started all parts in four consoles as described in the README.
### Loading and running a process
1. Go to the left dropdown menu and choose a process to load.
2. Click on "Load Process"
3. The corresponding workflow graph should appear below. You can zoom in/out and move it. Clicking on nodes dumps its 
   data structure as string into the textfield above (you might have to move the graph a bit down, so it gets visible).
4. Your loaded process should appear in the second dropdown menu. Choose it.
5. Click on "Add Containers to DB". This creates entries for all labware in that process in the positions described in
   the process in case there isn`t already labware. Existing labware is considered to belong to that process. You can 
   see all present labware in the database view which updates automatically.
6. (Optional) Click on "Schedule Process" to get a predicted schedule. It will appear at gantt chart.
7. Click on "Start Process". This will update the schedule and will execute steps accordingly.
   You can monitor the progress in the orchestrator GUI and the labware movements in the database view.
### Things to observe during the process
While the process runs you can observe different features of our framework.
1. Live updates of the process in the orchestrator:
   1. The gantt chart has a moving bar of where in time you currently are
   2. Process step nodes in the graph turn to yellow while they are being executed and to green when they are finished. Pink means there was an error.
   3. Labware is shown by barcode in the gantt chart as soon as a barcode is read/assigned
2. Live updates of the database
   1. In the database view which auto-reloads all labware is listed with barcode ans current position
   2. You can check and manipulate in the [admin view](http://127.0.0.1:8000/admin/) of the database what the results, duration, and starting times of which steps were and which labware was involved. The credentials are the ones you chose during the installation process for superuser.
3. View the movements of the robotic arm:
   1.