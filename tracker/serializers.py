from rest_framework import serializers
from .models import Employee, Task
from .validators import validate_title_content, validate_deadline_future


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

    # подключение валидаторов
    title = serializers.CharField(
        max_length=255,
        validators=[validate_title_content]
    )
    deadline = serializers.DateTimeField(
        validators=[validate_deadline_future]
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'parent_task', 'parent_task_title',
            'executor', 'executor_name', 'deadline', 'status'
        ]

    # валидация уровня объекта (связь нескольких полей)
    def validate(self, data):
        """ Проверка связей между полями.
        data - это словарь со всеми данными, которые пришли от пользователя """
        # получение статуса и исполнителя
        # get() нужен, так как пользователь может при обновлении (PATCH) не передать эти поля.
        status = data.get('status')
        executor = data.get('executor')

        # Если обновляем (PATCH), берем старые значения, если новые не передали
        if self.instance:
            # Если в запросе не прислали новый статус
            if status is None:
                # то берем старый статус из базы
                status = self.instance.status
                # аналогично с исполнителем
            if executor is None:
                executor = self.instance.executor

        if status == 'done' and not executor:
            raise serializers.ValidationError(
                {"status": "Нельзя завершить задачу без исполнителя. Назначьте кого-нибудь виноватым!"}
            )
        return data
