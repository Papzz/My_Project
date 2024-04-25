# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Копируем все файлы из текущей директории внутрь контейнера
COPY . .

# Команда для запуска приложения
CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]
