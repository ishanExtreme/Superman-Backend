import os
from datetime import timedelta

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

# set DJANGO_SETTINGS_MODULE with value task_manager.settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.config.local")

# The first argument to Celery is the name of the current module.
# This is only needed so that names can be automatically generated
# when the tasks are defined in the __main__ module.
app = Celery("task_manager")
app.config_from_object("django.conf:settings")
app.conf.enable_utc = False
# discovers new task from all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "send-message-every-day": {
        'task': 'schedule_message',
        'schedule': crontab(minute=00, hour=22)
    },
    "delete-due-tasks": {
        'task': 'delete_due_tasks',
        'schedule': crontab(minute=00, hour=00)
    }

}


def get_celery_worker_status():
    i = app.control.inspect()
    availability = i.ping()
    stats = i.stats()
    registered_tasks = i.registered()
    active_tasks = i.active()
    scheduled_tasks = i.scheduled()
    result = {
        'availability': availability,
        'stats': stats,
        'registered_tasks': registered_tasks,
        'active_tasks': active_tasks,
        'scheduled_tasks': scheduled_tasks
    }
    
    print(result)
    

get_celery_worker_status()