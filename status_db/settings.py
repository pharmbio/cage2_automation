from platform_status_db.larastatus.settings import *  # noqa: F403

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
