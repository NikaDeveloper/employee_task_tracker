# Employee Task Tracker API

### Система отслеживания задач сотрудников.

## Описание
REST API сервис для управления задачами и мониторинга загруженности сотрудников. Система позволяет создавать задачи, назначать исполнителей и автоматически находить подходящих кандидатов для важных задач.

## Технологии
* **Python 3.11**
* **Django 5.2 / Django REST Framework**
* **PostgreSQL** (в качестве БД)
* **Docker / Docker Compose** (контейнеризация)
* **drf-yasg** (Swagger/Redoc документация)
* **flake8** (Линтер)

## Как запустить

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/NikaDeveloper/employee_task_tracker
   cd employee_task_tracker
    ```

2. **Запустите проект через Docker:**
    ```bash
    docker-compose up --build -d
    ```

3. **Создайте суперпользователя (для доступа в админку):**
    ```bash
   docker exec -it tracker_app python manage.py createsuperuser 
   ```

## Документация API

*После запуска документация доступна по адресам:*

* Swagger: http://localhost:8000/swagger/

* ReDoc: http://localhost:8000/redoc/

## Основные эндпоинты

* /api/employees/ - управление сотрудниками
* /api/tasks/ - управление задачами
* /api/employees/busy_employees/ - список занятых сотрудников
* /api/tasks/important_tasks/ - поиск важных задач и рекомендации исполнителей

## Тестирование

Проект имеет высокое покрытие тестами (99%). Для запуска тестов выполните:

1. **Запуск тестов:**
   ```bash
   docker-compose exec app python manage.py test
   ```

2. Проверка покрытия кода (Coverage):
    ```bash
    docker-compose exec app coverage run --source='tracker' manage.py test
    docker-compose exec app coverage report
    ```

Автор: *Nika Developer*