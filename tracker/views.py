from rest_framework import viewsets
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count


class EmployeeViewSet(viewsets.ModelViewSet):
    """ CRUD для сотрудников """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(detail=False, methods=['get'])
    def busy_employees(self, request):
        """ Специальный эндпоинт: занятые сотрудники.
        Сортирует сотрудников по количеству активных задач (в работе) """
        # считаем только активные задачи in_progress
        active_tasks_count = Count('tasks', filter=Q(tasks__status='in_progress'))

        employees = Employee.objects.annotate(
            active_tasks_count=active_tasks_count
        ).order_by('-active_tasks_count')  # сортировка от тех, у кого число больше, к меньшим

        serializer = self.get_serializer(employees, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """ CRUD для задач """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=['get'])
    def important_tasks(self, request):
        """ Специальный эндпоинт: важные задачи.
        1. Задачи не в работе (for execution), но родительские для 'в работе(in progress)'.
         2. Подбор исполнителя """
        #  поиск важных задач
        important_tasks = Task.objects.filter(
            status='for execution',
            subtasks__status='in progress'
        ).distinct()

        # поиск наименее загруженного сотрудника
        least_loaded_employee = Employee.objects.annotate(
            active_tasks=Count('tasks', filter=Q(tasks__status='in progress'))
        ).order_by('active_tasks').first()

        result = []
        for task in important_tasks:
            candidate = least_loaded_employee.full_name if least_loaded_employee else "нет сотрудников"

            result.append({
                'id': task.id,
                'title': task.title,
                'deadline': task.deadline,
                'potential_executor': candidate
            })
        return Response(result)
