web: python manage.py migrate && gunicorn task_manager.wsgi
worker: REMAP_SIGTERM=SIGQUIT celery -A task_manager worker --loglevel=info
beat: REMAP_SIGTERM=SIGQUIT celery -A task_manager beat --loglevel=info