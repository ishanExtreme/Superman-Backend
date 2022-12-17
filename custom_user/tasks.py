from celery import shared_task
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from rest_framework.authtoken.models import Token
from tasks.models import Stage, Task

from tasks.utils import get_tasks_count

from twilio.rest import Client
import environ



# from celery.decorators import periodic_task
# from celery import shared_task
# from celery.schedules import crontab
# from django.utils.timezone import make_aware
# from django.db.models import Q

env = environ.Env()

account_sid = env('TWILIO_ACCOUNT_SID')
auth_token = env('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

User = get_user_model()

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1000})
def send_message(self, user_id):

    user = User.objects.get(id=user_id)
    current_date = date.today()
    next_date = current_date + timedelta(days=1)
    # Auth Token
    token, created = Token.objects.get_or_create(user=user)

    # get today's pending tasks count
    pending_tasks_today = get_tasks_count(token, False, current_date)

    # get tomorrow's pending tasks count
    pending_tasks_tomorrow = get_tasks_count(token, False, next_date)

    message = f"Your {pending_tasks_today} code is {pending_tasks_tomorrow}"

    number = env('TWILIO_NUMBER')
    res = client.messages.create(
        from_=f'whatsapp:{number}',
        body=message,
        to=f'whatsapp:+91{user.phone}'
    )

    return "send"


# def temp():
#     # get pending tasks
#     pending_tasks_today = show_tasks(token, False, current_date)
#     pending_tasks_tomorrow = show_tasks(token, False, next_date)

#     message = f"""
# Hi {user.username}, here are your pending tasks for today and tomorrow:
# *Few tasks that due today(I know you can complete them 😊)*:
# {pending_tasks_today}

# Due Tomorrow:
# {pending_tasks_tomorrow}

# Goodnight! Have a good day tomorrow!
#     """


@shared_task(name="schedule_message")
def schedule_message():

    # get all users with notification_on = True
    users = User.objects.filter(notification_on=True)

    for user in users:
        send_message.delay(user.id)

@shared_task(name="delete_due_tasks")
def delete_due_tasks():

    # get all users with reminder_board_id present
    users = User.objects.filter(reminder_board_id__isnull=False)

    # for each user delete tasks with today - due_date >= 2 and stage = reminder_board_id
    for user in users:
        stage = Stage.objects.get(id=user.reminder_board_id)
        Task.objects.filter(due_date__lte=date.today() - timedelta(days=2), stage=stage.id).delete()
            


