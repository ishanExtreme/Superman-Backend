from django.test import TestCase
from ..models import Schedule, Task, Stage, Board
import datetime

from django.contrib.auth import get_user_model
User = get_user_model()


class TaskTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )
        self.user.save()
        self.board = Board(title="Test Board", description="test", created_by=self.user)
        self.board.save()
        self.stage = Stage(title="Test", description="desc", created_by=self.user, board=self.board)
        self.stage.save()
        self.due_date = datetime.datetime.now()
        self.task = Task(title="Task with priority 1", priority=1, user=self.user, stage=self.stage, due_date=self.due_date)
        self.task.save()
        

    def test_str(self):
        """
        It should outputs the title of task
        """
        self.assertEqual(str(self.task), "Task with priority 1")

    def test_set_prev_state_and_get_prev_state(self):
        """
        value returned from getter methid should be equal to the value passed in
        setter method
        """
        self.task.set_prev_state(Task.STATUS_CHOICES[1][0])
        self.assertEqual(self.task.get_prev_state(), Task.STATUS_CHOICES[1][0])

    def test_handle_priority_on_adding_new_task(self):
        """
        A new task with same priotiry is added this should result in inrease of
        all the prev continious tasks priority
        """
        # Creating a new task with priority 1
        new_task = Task(title="Task with priority 1 Again", priority=1, user=self.user, stage=self.stage, due_date=self.due_date)
        new_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 1)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 2)

    def test_handle_priority_on_updating_prev_task(self):
        """
        A new task with priority 2 is added and prev tasks priority is updated to 2
        this should result in new task priority increased to 3
        """
        # Creating a new task with priority 2
        new_task = Task(title="Task with priority 2", priority=2, user=self.user, stage=self.stage, due_date=self.due_date)
        new_task.save()
        # update prev_task
        prev_task = Task.objects.get(id=self.task.id)
        prev_task.priority = 2
        prev_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 3)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 2)

    def test_handle_priority_on_adding_new_task_of_diff_user(self):
        """
        A new task with priority same as prev task is added but this time
        it is associated with a different user, hence no changes should be made
        on prev task
        """
        # Creating a new task with priority 1 and a new user
        new_user = User(
            username="user2", email="user2@django.com", password="welcome@123"
        )
        new_user.save()
        new_task = Task(
            title="Task with priority 1 Again and different user",
            priority=1,
            user=new_user,
            stage=self.stage, due_date=self.due_date
        )
        new_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 1)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 1)

    def test_handle_priority_on_updating_completed_task(self):
        """
        A new task is created with priority 2 and now its updated to priorty 1 and
        completed to true, this should not effect the priority of prev task
        """
        # Creating a new task with priority 1
        new_task = Task(title="Task with priority 2", priority=2, user=self.user, stage=self.stage, due_date=self.due_date)
        new_task.save()
        # updating new task
        new_task.priority = 1
        new_task.completed = True
        new_task.save()
        # get new task from database
        new_task = Task.objects.get(id=new_task.id)
        self.assertEqual(new_task.priority, 1)
        # get prev task from database
        prev_task = Task.objects.get(id=self.task.id)
        self.assertEqual(prev_task.priority, 1)




class ScheduleTest(TestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )
        self.user.save()
        self.schedule = Schedule(user=self.user, time="02:00:00")
        self.schedule.save()

    def test_str(self):
        """
        It should print the daily schedule of the user
        """
        self.assertEqual(str(self.schedule), f"Schedule for 02:00:00 daily")
