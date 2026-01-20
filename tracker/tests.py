from .models import Employee, Task
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
import datetime


class EmployeeTests(APITestCase):
    def setUp(self):
        """ Подготовка данных перед каждым тестом """
        self.employee = Employee.objects.create(
            full_name="Иван Тестовый",
            position="Менеджер"
        )
        self.list_url = reverse('employee-list')

    def test_create_employee(self):
        """ Тест создания сотрудника """
        data = {
            "full_name": "Новый сотрудник",
            "position": "Middle",
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)
        self.assertEqual(Employee.objects.last().full_name, "Новый сотрудник")

    def test_get_employees_list(self):
        """ Тест получения списка """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class TaskTests(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(full_name="Иван", position="Dev")
        # ддл завтра
        self.future_date = timezone.now() + datetime.timedelta(days=1)
        self.task = Task.objects.create(
            title="Тестовая задача",
            deadline=self.future_date,
            executor=self.employee,
            status="for execution"
        )
        self.list_url = reverse('task-list')

    def test_create_task(self):
        """ Тест создания задачи """
        data = {
            "title": "Новая задача",
            "deadline": self.future_date,
            "status": "for execution"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_update_task(self):
        """ Тест обновления задачи """
        url = reverse('task-detail', args=[self.task.id])
        data = {"title": "Обновленное название"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Обновленное название")


class ValidatorTests(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(full_name="Иван", position="Dev")
        self.list_url = reverse('task-list')

    def test_create_task_with_forbidden_word(self):
        """ Тест задачи с запрещенным словом """
        data = {
            "title": "Это полная ерунда",  # Слово из списка запрещенных
            "deadline": timezone.now() + datetime.timedelta(days=1),
            "status": "for execution"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_create_task_past_deadline(self):
        """ Тест создания задачи в прошлом """
        past_date = timezone.now() - datetime.timedelta(days=1)
        data = {
            "title": "Нормальная задача",
            "deadline": past_date,
            "status": "for execution"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('deadline', response.data)

    def test_close_task_without_executor(self):
        """ Тест на закрытие задачи без исполнителя """
        # создание задачи без исполнителя
        task = Task.objects.create(
            title="Задача без автора",
            deadline=timezone.now() + datetime.timedelta(days=1),
            executor=None,
            status='for execution'
        )

        url = reverse('task-detail', args=[task.id])
        # попытка поставить статус done
        data = {"status": "done"}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # ошибка должна быть в поле status (так как это прописано в сериализаторе)
        self.assertIn('status', response.data)


class SpecialEndpointsTests(APITestCase):
    """ Тест Busy Employees и Important Tasks """

    def setUp(self):
        # Иван (занят)
        self.ivan = Employee.objects.create(full_name="Иван", position="Junior")
        # Петр (свободен)
        self.petr = Employee.objects.create(full_name="Петр", position="Senior")

        self.future = timezone.now() + datetime.timedelta(days=5)

        # даем Ивану задачу "В работе"
        Task.objects.create(
            title="Задача Ивана",
            executor=self.ivan,
            status='in progress',
            deadline=self.future
        )

        # создаем "важную задачу" (родительская, не в работе)
        self.parent_task = Task.objects.create(
            title="Важный фундамент",
            status='for execution',  # не взята
            deadline=self.future,
            executor=None
        )

        # создание зависимой задачи, которая УЖЕ в работе (делает Иван)
        Task.objects.create(
            title="Стены",
            status='in progress',
            parent_task=self.parent_task,
            executor=self.ivan,
            deadline=self.future
        )

    def test_busy_employees(self):
        """ Проверка сортировки занятых сотрудников """
        url = reverse('employee-busy-employees')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # Иван должен быть первым, так как у него есть активная задача
        self.assertEqual(data[0]['full_name'], "Иван")
        # Петр должен быть вторым
        self.assertEqual(data[1]['full_name'], "Петр")

    def test_important_tasks(self):
        """ Проверка поиска важных задач """
        url = reverse('task-important-tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], "Важный фундамент")

        # Проверяем, что система предлагает Петра (он свободен)
        # (Либо Ивана, если логика "родительскую делает тот же, кто дочернюю",
        # но в нашем коде мы искали least_loaded, а Петр имеет 0 задач, Иван 2)
        self.assertEqual(data[0]['potential_executor'], "Петр")

