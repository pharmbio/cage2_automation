#! /bin/bash

cd platform_status_db/platform_status_db
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
cd ../..