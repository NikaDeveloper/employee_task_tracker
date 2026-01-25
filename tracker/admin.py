from django.contrib import admin
from .models import Employee, Task


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position')
    search_fields = ('full_name', 'position')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'executor', 'deadline', 'status')
    search_fields = ('status', 'deadline')
