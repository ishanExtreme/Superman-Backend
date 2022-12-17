import requests
import re
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
User = get_user_model()

import environ

env = environ.Env()

base_url = env("BASE_URL", default="http://127.0.0.1:8000/api/")

error_msg = "Error in processing your request, please try again later."

def make_request(url, method, body, token):
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json; charset=utf-8"}
    if(method == "get"):
            response = requests.get(base_url+url, headers=headers)
            if(response.ok):
                return response.json()
            else:
                raise Exception
    if(method == "post"):
        response = requests.post(base_url+url, json=body ,headers=headers)
        if(response.ok):
            return response.json()
        else:
            raise Exception

def help(message):

    if(message == "list all boards"):
        return "This command will display all boards in your account."

    if(message == "create board"):
        return """
To create a new board send: *Create board title:<board title>$ desc:<board description>$*

example to create a board with title _title-1_ and description _desc-1_

*Create board title:title-1$ desc:desc-1$*

_Note: do include "$" after title end and description end_
        """

    if("list all stages" in message):
        return """
To list all stages of a particular board send: *List all stages from board:<board uid>$*

example to get all stages from board with uid _1_

*List all stages from board:1$*

_Note: to get uid of a board you can use "list all boards" command_
_Note: dollar at the end is must_
        """

    if("create stage" in message):
        return """
To create a new stage in particular bord: *Create stage board:<board_uid>$ title:<stage title>$ desc:<stage description>$*

example to create a stage in bord with board_id _1_, stage title is _title-1_ and description is _desc-1_

*Create stage board:1$ title:title-1$ desc:desc-1$*

_Note: to get uid of a board you can use "list all boards" command_
_Note: dollars at position given is must_
        """

    if(message == "list all tasks"):
        return """
This command will display all tasks(complete or incomplete) in your account.

To display all complete tasks: **List all complete tasks**

To display all incomplete tasks: **List all incomplete tasks**
"""

    if(message == "list all tasks from board"):
        return """
This command will display all tasks from a particular board.

To display all tasks from a particula board: *List tasks from board:<board uid>$*

example to display all tasks from board with uid _1_

*List tasks from board:1$*

_Note: to get uid of a board you can use "list all boards" command_
_Note: dollar at the end is must_
        """

    if(message == "preview task"):
        return """
This command displays details a particular task.

To get details of a particular task: *Preview task:<task uid>$*

example to preview task with uid _1_

*Preview task:1$*

_Note: to get uid of a task you can use any task listing command_
_Note: dollar at the end is must_
        """

    if("create task" in message):
        return """
This command create task.

To create a task: *Create task title:<task title>$ desc:<task description>$ priority:<task priority>$ stage:<stage uild>$ due_date:<task's due date>$*

example to create a task with title _task title_ and description with _task desc_ and priority with _1_ stage set to _1_ and due_date is _2022-11-30_

*Create task title:task title$ desc:task desc$ priority:1$ stage:1$ due_date:2022-11-30$*
        """

def show_all_boards(token):

    res = None
    try:
        res = make_request("board", "get", None, token)
    except:
       return error_msg

    if(len(res) == 0):
        return "Board list empty."

    message = ""
    for idx, board in enumerate(res):
        title = board.get("title")
        uid = board.get("id")
        message = message + f"{idx+1}. *{title}* (uid:_{uid}_)\n\n"

    return message

def create_board(title, desc, token):

    body = {"title":title, "description":desc}
    res = None
    try:
        res = make_request("board/", "post", body, token)
    except:
        return error_msg

    return f"Succesfully creted board with title {title} and description {desc}."

def show_stages(board_id, token):

    url = f"board/{board_id}/stage"
    res = None
    try:
        res = make_request(url, "get", None, token)
    except:
        return error_msg
    
    if(len(res) == 0):
        return "Stage list empty."

    message = ""
    for idx, stage in enumerate(res):
        title = stage.get("title")
        uid = stage.get("id")
        message = message + f"{idx+1}. *{title}* (uid:_{uid}_)\n\n"

    return message

def create_stage(board_id, title, desc, token):

    body={"title":title, "description":desc, "board":board_id}
    res = None

    try:
        res = make_request("stage/", "post", body, token)
    except:
        return error_msg

    return f"Succesfully created stage with title {title} and description {desc}."

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
        
# due_date is in format yyyy-mm-dd
def show_tasks(token, complete, due_date=None):

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

    if(len(res) == 0):
        return "Task list empty."

    message = ""
    # pretty message
    for idx, task in enumerate(res):
        title = task.get("title")
        uid = task.get("id")
        message = message + f"{idx+1}. *{title}* (uid:_{uid}_)"
        completed = task.get("completed")
        if completed:
            message = message+"✅\n"
        else:
            message = message+"⏳\n"
        message = message + "\n"

    return message

def show_tasks_of_board(board_id, token):

    url = f"board/{board_id}/task"
    res = None

    try:
        res = make_request(url, "get", None, token)
    except:
        return error_msg

    if(len(res) == 0):
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




def process_message(name, message, phone):

    user = None
    try:
        user = User.objects.get(phone = phone)
        if(user.wa_sending == False):
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
    message = message.lower()

    # Hi message
    if(message == "hi" or message == "hello" or message == "hey"):
        return f"""
Hello, {name} this is SuperTaskManager at your service, here are somethings you can use me for.
*Feature: Command*
*1. To list all boards:* _List all boards_

*2. To create a new board:* _Create board title:<board title>$ desc:<board description>$_

*3. To list all stages in a particular board:*_List all stages from board:<board uid>$_

*4. To create a new stage in a particular board:*_Create stage board:<board_uid>$ title:<stage title>$ desc:<stage description>$_

*5. Show all complete/incomplete tasks:*_List all complete/incomplete tasks_

*6. Show all tasks from a prticular board:*_List tasks from board:<board uid>$_

*7. Preview a particular task:*_Preview task:<task uid>$_

*8. Create a task:*_Create task title:<task title>$ desc:<task description>$ priority:<task priority>$ stage:<stage uild>$ due_date:<task's due date>$_
        """

    # show all boards message
    if("list" in message and 
    ("all" in message or "every" in message) and 
    ("boards" in message or "board" in message) and 
    ("stage" not in message or "stages" not in message) and
    ("task" not in message or "tasks" not in message)):
        return show_all_boards(token)
    
    # Create a new board
    if("create" in message and "board" in message and ("stage" not in message or "stages" not in message)):
        syntax_correct = re.search("create board title:.*\$ desc:.*\$.*", message)
        if(not syntax_correct):
            return help("create board")

        title = message[message.find("title")+6:message.find("$")]
        desc = message[message.find("desc")+5:message.find("$", message.find("desc"))]
        return create_board(title, desc, token)

    # List all stages in a board
    if("list" in message and ("all" in message or "every" in message) and ("stages" in message or "stage" in message)):
        syntax_correct = re.search("list all stages from board:.*\$.*", message)
        if(not syntax_correct):
            return help("list all stages")
        
        board_id = message[message.find("board")+6:message.find("$")]
        return show_stages(board_id, token)

    # create a stage in a board
    if("create" in message and "stage" in message and ("task" not in message or "tasks" not in message)):
        syntax_correct = re.search("create stage board:.*\$ title:.*\$ desc:.*\$.*", message)
        if(not syntax_correct):
            return help("create stage")

        board_id = message[message.find("board")+6:message.find("$")]
        title = message[message.find("title")+6:message.find("$", message.find("title"))]
        desc = message[message.find("desc")+5:message.find("$", message.find("desc"))]

        return create_stage(board_id, title, desc, token)

    # list all tasks
    if("list" in message and ("tasks" or "task") in message and ("board" or "boards") not in message):
        syntax_correct = re.search("list all complete|incomplete tasks.*", message)
        if(not syntax_correct):
            return help("list all tasks")

        complete = True
        if("incomplete" in message):
            complete = False

        return show_tasks(complete, token)

    if("list" in message and ("tasks" or "task") in message and "board" in message):
        syntax_correct = re.search("list tasks from board:.*\$.*", message)
        if(not syntax_correct):
            return help("list all tasks from board")
        
        board_id = message[message.find("board")+6:message.find("$")]

        return show_tasks_of_board(board_id, token)

    if("preview" in message and ("task" or "tasks") in message):
        syntax_correct = re.search("preview task:.*\$.*", message)
        if(not syntax_correct):
            return help("preview task")

        task_id = message[message.find("task")+5:message.find("$")]

        return preview_task(task_id, token)

    # if("create" in message and "task" in message):
    #     syntax_correct = re.search("Create task title:.*\$ desc:.*\$ priority:.*\$ stage:.*\$ due_date:.*\$")
    #     if(not syntax_correct):                          

        






    
