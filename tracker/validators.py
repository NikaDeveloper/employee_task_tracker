from rest_framework import serializers
from django.utils import timezone


def validate_title_content(value):
    """ Валидатор: запрещает использовать слова-паразиты в названии """
    forbidden_words = ['фигня', 'ерунда', 'что-то', 'дичь', 'не знаю', 'мусор']
    value_lower = value.lower()
    for word in forbidden_words:
        if word in value_lower:
            raise serializers.ValidationError(f"Заголовок не может содержать слово '{word}'. Будьте профессиональнее!")


def validate_deadline_future(value):
    """ Валидатор: дата дедлайна не может быть в прошлом """
    # timezone.now() - возвращает текущее время с учетом часового пояса
    if value < timezone.now():
        raise serializers.ValidationError("Дедлайн не может быть в прошлом. Машину времени еще не изобрели!")
