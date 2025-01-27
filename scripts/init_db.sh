#! /bin/bash

cd source || exit
cd platform_status_db/platform_status_db || exit
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
cd ../..