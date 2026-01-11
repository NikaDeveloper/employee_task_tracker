from rest_framework import serializers
from .models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    """ Сериализатор для сотрудников """
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position']


class TaskSerializer(serializers.ModelSerializer):
    """ Сериализатор для задач """
    # эти поля нужны, чтобы в API видеть имена, а не просто ID
    executor_name = serializers.ReadOnlyField(source='executor.full_name')
    parent_task_title = serializers.ReadOnlyField(source='parent_task.title')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'parent_task', 'parent_task_title',
            'executor', 'executor_name', 'deadline', 'status'
        ]
