from django.db import models


class Employee(models.Model):
    """ Модель сотрудника """
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    position = models.CharField(max_length=100, verbose_name='Должность')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.full_name


class Task(models.Model):
    """ Модель задачи """
    STATUS_CHOICES = [
        ('for execution', 'к выполнению'),
        ('in progress', 'в процессе'),
        ('done', 'завершено'),
    ]

    title = models.CharField(max_length=255, verbose_name='Наименование')

    # ссылка на родительскую задачу
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,  # задача может быть основной (без родителя)
        blank=True,
        related_name='subtasks',
        verbose_name='Родительская задача'
    )

    # Исполнитель (связь с сотрудником)
    executor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Исполнитель'
    )

    deadline = models.DateTimeField(verbose_name='Срок')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='for execution',
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title
