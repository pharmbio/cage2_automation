###
# Script to open several console tabs and start all tool required to use the lab-automation software collection
# It will only work when all software was installed and the default virtual environment exists
###

gnome-terminal --tab -- bash -ic "source venv/lab_automation/bin/activate; cd lara_implementation/lara_processes; python start_script.py; exec bash;"
gnome-terminal --tab -- bash -ic "source venv/lab_automation/bin/activate; cd lara_server_tools/lara_simulation/lara_simulation; python dash_app.py; exec bash;"
gnome-terminal --tab -- bash -ic "source venv/lab_automation/bin/activate; cd lara_server_tools/lara_simulation/lara_simulation; python start_visualization.py; exec bash;"
gnome-terminal --tab -- bash -ic "source venv/lab_automation/bin/activate; cd platform_status_database/platform_status_db; python manage.py runserver; exec bash;"
gnome-terminal --tab -- bash -ic "source venv/lab_automation/bin/activate; python -m scheduler_server --insecure -p 50066; exec bash;"
gnome-terminal --tab -- bash -ic "source venv/lab_automation/bin/activate; exec bash;"

