# Использовать официальный базовый образ Python
FROM python:3.10.6

# Задать переменные среды
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Задать рабочий каталог
WORKDIR /code

# Копировать файл зависимостей
COPY requirements.txt /code

# Установить зависимости
RUN pip install --upgrade pip && \
    pip install -r /code/requirements.txt

# Установить дополнительные пакеты
RUN apt-get update && apt-get install -y gunicorn3

# Копировать папку watermarks в папку media внутри контейнера
# Предполагается, что папка watermarks находится в контексте сборки
COPY watermarks/ /code/media/

# Далее можете добавить остальные команды для конфигурации вашего приложения