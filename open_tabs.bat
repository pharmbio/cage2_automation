start cmd /k  & cd lara_implementation\lara_processes & python start_script.py
start cmd /k  & cd lara_server_tools\lara_simulation\lara_simulation & python dash_app.py
start cmd /k  & cd lara_server_tools\lara_simulation\lara_simulation & python visualize_from_json.py
start cmd /k  & cd platform_status_database\platform_status_db & python manage.py runserver
start cmd /k  & python -m scheduler_server --insecure -p 50066