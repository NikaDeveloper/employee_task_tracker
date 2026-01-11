FROM python:3.11-slim

WORKDIR /app

# запрет для python писать файлы .рус на диск и включение буферицации логов
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# установка системных зависимостей для работы с psycopg-2(драйвера бд)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
