from rest_framework.test import APITestCase, force_authenticate
from ..models import Task, Stage, Board
import datetime
from django.test import RequestFactory
from ..apiviews import (
    ChangePasswordView
)
from django.core import mail

from django.contrib.auth import get_user_model
User = get_user_model()


class UserFunctionalityTest(APITestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne",
            email="bruce@wayne.org",
        )
        self.user.save()
        self.user.set_password("i_am_batman")
        self.user.save()

    def test_change_password_with_correct_old_password(self):
        new_pass = "Ishan@2605"
        request = RequestFactory().patch("/api/change-password/",
                                         {"old_password": "i_am_batman", "new_password": "Ishan@2605"}, content_type='application/json')
        force_authenticate(request, user=self.user)
        response = ChangePasswordView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.check_password(new_pass), True)

    def test_change_password_with_incorrect_password(self):
        new_pass = "Welcome@123"
        request = RequestFactory().patch("/api/change-password/",
                                         {"old_password": "welcome2233", "new_password": new_pass}, content_type='application/json')
        force_authenticate(request, user=self.user)
        response = ChangePasswordView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_reset_password_with_correct_token(self):
        new_pass = "Welcome@123"
        self.client.post("/api/password-reset/", {"email": self.user.email})
        token = mail.outbox[0].body.split(" ")[-1]
        res = self.client.post(
            "/api/password-reset/confirm/", {"token": token, "password": new_pass})
        self.assertEqual(res.status_code, 200)
        user = User.objects.get(email=self.user.email)
        self.assertEqual(user.check_password(new_pass), True)

    def test_reset_password_with_false_token(self):
        new_pass = "Welcome@123"
        self.client.post("/api/password-reset/", {"email": self.user.email})
        token = "2132231"
        res = self.client.post(
            "/api/password-reset/confirm/", {"token": token, "password": new_pass})
        self.assertEqual(res.status_code, 404)
        user = User.objects.get(email=self.user.email)
        self.assertEqual(user.check_password(new_pass), False)

    # def test_reset_password_with_auth(self):
    #     self.client.login(username="bruce_wayne", password="i_am_batman")
    #     response = self.client.get("/api/password-reset/")
    #     self.assertEqual(response.status_code, 200)


class TaskViewSetTest(APITestCase):
    def setUp(self):
        self.user = User(
            username="bruce_wayne",
            email="bruce@wayne.org",
        )
        self.user.save()
        self.user.set_password("i_am_batman")
        self.user.save()
        self.board = Board(title="Test Board",
                           description="test", created_by=self.user)
        self.board.save()
        self.stage = Stage(title="Test", description="desc",
                           created_by=self.user, board=self.board)
        self.stage.save()
        self.task1 = Task(title="Task with title 1", priority=1, user=self.user,
                          due_date=datetime.datetime.now(), stage=self.stage)
        self.task1.save()
        self.task2 = Task(
            title="Task with title 2", priority=2, user=self.user, deleted=True, due_date=datetime.datetime.now(), stage=self.stage
        )
        self.task2.save()
        user2 = User(username="ishan", email="ishan@wayne.org",
                     password="welcome@123")
        user2.save()
        self.task3 = Task(
            title="Task with title 3 and of user 2", priority=2, user=user2, due_date=datetime.datetime.now(), stage=self.stage
        )
        self.task3.save()
        self.client.login(username="bruce_wayne", password="i_am_batman")

    def test_deletd_tasks_are_not_returned(self):
        response = self.client.get("/api/task/")
        self.assertEqual(len(response.data), 1)

    def test_other_users_tasks_cannot_be_seen(self):
        response = self.client.get(f"/api/task/{self.task3.id}/")
        self.assertEqual(response.status_code, 401)

    def test_other_users_tasks_cannot_be_updated(self):
        response = self.client.put(
            f"/api/task/{self.task3.id}/",
            {"title": "Temporary Task", "description": "random", "priority": 1},
        )
        self.assertEqual(response.status_code, 401)

    def test_other_users_tasks_cannot_be_deleted(self):
        response = self.client.delete(f"/api/task/{self.task3.id}/")
        self.assertEqual(response.status_code, 401)
