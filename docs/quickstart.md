# Quickstart Guide

This guide lists the steps to load and run a process assuming you already started all parts in four consoles as described in the README.
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