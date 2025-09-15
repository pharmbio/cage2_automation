from platform_status_db.larastatus.settings import *  # noqa: F403

import os

if os.name == "posix":
    db_host = "172.17.0.1"
else:
    db_host = "host.docker.internal"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "platform_status_db",
        "USER": "platform_status",
        "PASSWORD": "platform_status",
        "HOST": "172.17.0.1",
        "PORT": "5432",
    }
}
