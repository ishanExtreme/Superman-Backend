from celery import shared_task
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from rest_framework.authtoken.models import Token

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


def send_message(user):

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

    return res


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
    print("in")
    users = User.objects.filter(notification_on=True)

    for user in users:
        send_message(user)
