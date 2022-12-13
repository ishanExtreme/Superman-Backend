import environ
import datetime
import requests
import re
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from tasks.models import Stage
User = get_user_model()


env = environ.Env()

base_url = env("BASE_URL")

error_msg = "Error in processing your request, please try again later."


def make_request(url, method, body, token):
    headers = {"Authorization": f"Token {token}",
               "Content-Type": "application/json; charset=utf-8"}
    if (method == "get"):
        response = requests.get(base_url+url, headers=headers)
        if (response.ok):
            return response.json()
        else:
            raise Exception
    if (method == "post" or method == "put" or method == "delete" or method == "patch"):

        response = None
        if method == "post":
            response = requests.post(base_url+url, json=body, headers=headers)
        elif method == "put":
            response = requests.put(base_url+url, json=body, headers=headers)
        elif method == "delete":
            response = requests.delete(base_url+url, headers=headers)
        elif method == "patch":
            response = requests.patch(base_url+url, json=body, headers=headers)

        if (response and response.ok):
            return response.json()
        else:
            raise Exception


def create_task(title, due_date, stage_id, token):
    """
    This function creates a task in account with given title and due_date.
    """
    url = "task/"
    body = {
        "title": title,
        "description": "Created through Whatsapp",
        "priority": 1,
        "due_date": due_date,
        "stage": stage_id
    }
    res = None

    try:
        res = make_request(url, "post", body, token)
    except:
        return error_msg

    return f"Reminder to _{title}_ succesfully added to your list."


def get_tasks_count(token, complete, due_date=None):
    """
    This function returns number of tasks in account with filter of complete and due_date.
    """
    url = None
    if due_date:
        url = f"task?completed={complete}&due_date={due_date}"
    else:
        url = f"task?completed={complete}"
    res = None

    try:
        res = make_request(url, "get", None, token)
    except:
        return error_msg

    return len(res)


def show_tasks_of_board(board_id, token):

    url = f"board/{board_id}/task"
    res = None

    try:
        res = make_request(url, "get", None, token)
    except:
        return error_msg

    if (len(res) == 0):
        return "Task list empty."
    stage_tasks = {}

    for task in res:
        stage_tasks[task["stage_name"]] = []
    for task in res:
        stage_tasks[task["stage_name"]].append(task)

    message = ""
    for stage, tasks in stage_tasks.items():
        message = message + f"{stage} 📋\n"

        for task in tasks:
            title = task.get("title")
            uid = task.get("id")
            completed = task.get("completed")

            message = message + f"*{title}* (uid:_{uid}_) "
            if completed:
                message = message+"✅\n"
            else:
                message = message+"⏳\n"
        message = message + "\n"

    return message


def change_task_status(task_id, status, token):
    """
    This function changes the status of task with given id.
    """
    url = f"task/{task_id}/"
    body = {
        "completed": status
    }
    res = None

    try:
        res = make_request(url, "patch", body, token)
    except:
        return error_msg

    msg = "completed" if status else "pending"
    return f"Task status changed to {msg}."


def preview_task(task_id, token):

    url = f"task/{task_id}"
    res = None

    try:
        res = make_request(url, "get", None, token)
    except:
        return error_msg

    title = res.get("title")
    desc = res.get("description")
    priority = res.get("priority")
    completed = res.get("completed")
    stage_name = res.get("stage_name")
    due_date = res.get("due_date")

    # formatting due_date
    due_date = datetime.datetime.strptime(
        due_date, "%Y-%m-%d").strftime("%d %b %Y")

    if completed:
        completed = "✅"
    else:
        completed = "⏳"

    message = f"""
*Title:* _{title}_

*Description:* _{desc}_

*Priority:* _{priority}_

*Completed:* {completed}

*Stage:* _{stage_name}_

*Due Date:* _{due_date}_
    """

    return message


def help(message):
    if message == "help reminder":
        return """
To create reminder for a task: *Hey, remind me to <task> today/tomorrow/<yyyy-mm-dd>*

example1: *Hey, remind me to buy milk today*
example2: *Hey, remind me to recharge TV on 2022-12-23*

_Note: date format is strictly yyyy-mm-dd_
        """

    if message == "help list":
        return """
To list all pending and completed tasks: *Hey, list all my tasks*

example1: *Hey, list all my tasks*

_Note: this will only list tasks in user's whatsapp board_
        """

    if message == "mark complete":
        return """
To mark a task as complete: *Hey, mark task <uid> as complete*

example1: *Hey, mark task 1 as complete*

_Note: You can get the uid of a task by listing all tasks_
        """

    if message == "help preview":
        return """
To preview a task: *Hey, preview task <uid>*

example1: *Hey, preview task 1*

_Note: You can get the uid of a task by listing all tasks_
        """


def process_message(name, message, phone):

    user = None
    try:
        user = User.objects.get(phone=phone)
        if (user.wa_sending == False):
            raise Exception
    # if WA feature is not enables
    except:
        return f"""
*Whastapp feature not enabled in your account*
Hi, {name}
There's a little problem, but no worries, we can solve it together! I have listed the step below that you have to follow in order to enable whatsapp feature for your super task manager.
Step1: Login to your account
Step2: Click on your profile picture
Step3: Go to settings and enable whatsapp feature
Will meet you after this!!!
"""

    # generate auth token
    token, created = Token.objects.get_or_create(user=user)
    reminder_board_id = user.reminder_board_id
    stage_id = Stage.objects.get(board=reminder_board_id, title="Reminders").id
    message = message.lower()

    # Hi message
    if (message == "hi" or message == "hello" or message == "hey"):
        return f"""
Hello, {name} this is SuperTaskManager at your service, here are few you can use me for.
*Feature: Command*
*1. To create a reminder:* _Hey, remind me to <task> today/tomorrow/<yyyy-mm-dd>_
type *help reminder* to know more.

*2. To list all pending/completed tasks:* _Hey, list all my tasks_
type *help list* to know more.

*3. To mark a task as completed:* _Hey, mark task <uid> as complete_
type *help mark complete* to know more.

*4. To preview a task:* _Hey, preview task <uid>_
type *help preview* to know more.
        """

    if "remind" in message:
        # regex to check Hey, remind me to <task> today/tomorrow/<yyyy-mm-dd>
        if (re.search(r"^hey, remind me to (.*) (today|tomorrow|\d{4}-\d{2}-\d{2})$", message)):
            task = message.split("to")[1].strip()
            date = message.split(" ")[-1]

            # sanitize task title
            if task.split(" ")[-1] == date:
                # remove on from task title
                task = task.split("on")[0].strip()

            if date == "today":
                date = datetime.date.today().strftime("%Y-%m-%d")
            elif date == "tomorrow":
                date = (datetime.date.today() +
                        datetime.timedelta(days=1)).strftime("%Y-%m-%d")

            res = create_task(task, date, stage_id, token)
            return res
        else:
            return help("help reminder")

    if "list" in message:
        # regex to check Hey, list all my pending/completed tasks
        if (re.search(r"^hey, list all my tasks$", message)):

            res = show_tasks_of_board(reminder_board_id, token)
            return res
        else:
            return help("help list")

    if "mark" in message:
        # regex to check Hey, mark task <uid> as complete
        if (re.search(r"^hey, mark task (\d+) as complete$", message)):
            task_id = message.split(" ")[-3]
            res = change_task_status(task_id, True, token)
            return res
        else:
            return help("help mark complete")

    if "preview" in message:
        # regex to check Hey, preview task <uid>
        if (re.search(r"^hey, preview task (\d+)$", message)):
            task_id = message.split(" ")[-1]
            res = preview_task(task_id, token)
            return res
        else:
            return help("help preview")

    return """
I wasn't able to understand your message, please type *Hi* to know all the things I can do for you.
    """
