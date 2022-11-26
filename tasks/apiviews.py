from django.contrib.auth.models import User
from tasks.models import Task, History, Board, Stage
from rest_framework.serializers import (
    ModelSerializer,
    EmailField,
    CharField,
    StringRelatedField,
)
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
    ChoiceFilter,
    BooleanFilter,
    DateFilter,
)
from rest_framework import status


class TaskCompletedCountView(APIView):
    """
    A view that returns the count of tasks.
    """

    renderer_classes = (JSONRenderer,)
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        task_count = Task.objects.filter(completed=True).count()
        content = {"count": task_count}
        return Response(content)


class TaskIncompleteCountView(APIView):
    """
    A view that returns the count of tasks.
    """

    renderer_classes = (JSONRenderer,)
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        task_count = Task.objects.filter(completed=False).count()
        content = {"count": task_count}
        return Response(content)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class UserCreationSerializer(ModelSerializer):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Register User
class UserCreation(mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (AllowAny,)


# Get user via token
class UserGet(mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)


class BoardSerializer(ModelSerializer):
    title = CharField(min_length=3, max_length=255)

    class Meta:
        model = Board
        fields = ["id", "title", "description"]


class StageSerializer(ModelSerializer):
    title = CharField(min_length=3, max_length=255)
    board_name = StringRelatedField(source="board", read_only=True)

    class Meta:
        model = Stage
        fields = ["id", "title", "description", "board_name"]


class StageSerializerSuper(ModelSerializer):
    title = CharField(min_length=3, max_length=255)
    board_name = StringRelatedField(source="board", read_only=True)

    class Meta:
        model = Stage
        fields = ["id", "title", "description", "board", "board_name"]


class TaskSerializer(ModelSerializer):
    stage_name = StringRelatedField(source="stage", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "completed",
            "stage_name",
            "due_date",
            "created_date",
        ]


class TaskSerializerSuper(ModelSerializer):
    stage_name = StringRelatedField(source="stage", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "stage",
            "completed",
            "stage_name",
            "due_date",
            "created_date",
        ]


class HistorySerializer(ModelSerializer):
    class Meta:
        model = History
        fields = ["task", "previous_status", "new_status", "changed_at"]


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    completed = BooleanFilter()
    due_date = DateFilter()


class HistoryFilter(FilterSet):
    changed_at = DateFilter()
    previous_status = ChoiceFilter(choices=Task.STATUS_CHOICES)
    new_status = ChoiceFilter(choices=Task.STATUS_CHOICES)


class BoardFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BoardFilter

    def get_queryset(self):
        return Board.objects.filter(deleted=False, created_by=self.request.user)

    def perform_create(self, serializer):
        # serializer.user = self.request.user
        # serializer.save()
        serializer.save(created_by=self.request.user)


class StageListView(mixins.ListModelMixin, GenericViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # from nested router doc
        # __ looks into the field of the foreign key
        return Stage.objects.filter(
            deleted=False, board=self.kwargs["board_pk"], created_by=self.request.user
        )


class StageViewSet(ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializerSuper
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # from nested router doc
        # __ looks into the field of the foreign key
        return Stage.objects.filter(deleted=False, created_by=self.request.user)

    def perform_create(self, serializer):
        # serializer.user = self.request.user
        # serializer.save()
        serializer.save(created_by=self.request.user)


class TaskViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(
            deleted=False, stage=self.kwargs["stage_pk"], user=self.request.user
        ).order_by("priority")


class TaskViewSetSuper(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializerSuper
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "completed", "priority"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HistroryViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HistoryFilter

    def get_queryset(self):
        # from nested router doc
        # __ looks into the field of the foreign key
        return History.objects.filter(
            task=self.kwargs["task_pk"], task__user=self.request.user
        )


######################## User password update logic ##############################

class ChangePasswordSerializer(ModelSerializer):
    """
    Serializer for user password change view
    """
    old_password = CharField(required=True)
    new_password = CharField(required=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password"]

class ChangePasswordView(generics.UpdateAPIView):
    """
    Endpoint to change user's password having current password in hand
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        obj = self.request.user
        return obj

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not instance.check_password(serializer.data.get("old_password")):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        instance.set_password(serializer.data.get("new_password"))
        instance.save()
        response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

        return Response(response)
        

