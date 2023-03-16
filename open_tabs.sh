gnome-terminal --tab -- bash -ic "cd lara_implementation/lara_processes; python start_script.py; exec bash;"
gnome-terminal --tab -- bash -ic "cd lara_server_tools/lara_simulation/lara_simulation; python dash_app.py; exec bash;"
gnome-terminal --tab -- bash -ic "cd lara_server_tools/lara_simulation/lara_simulation; python start_visualization.py; exec bash;"
gnome-terminal --tab -- bash -ic "cd platform_status_database/platform_status_db; python manage.py runserver; exec bash;"
gnome-terminal --tab -- bash -ic "python -m scheduler_server --insecure -p 50066; exec bash;"

