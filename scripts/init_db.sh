#! /bin/bash

cd platform_status_db/src/platform_status_db || exit
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
cd ../../..
