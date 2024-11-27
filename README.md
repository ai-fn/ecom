# E-commerce платформа

- ## Документация
    Подробная документация доступна в [GitLab Wiki](https://gitlab.altawest.ru/products/megashop/shop-backend/-/wikis/home).


- ## Запуск окружения разработчика
  1. **Клонируем репозиторий**
      ```bash
      git clone https://gitlab.altawest.ru/products/megashop/shop-backend
      ```
  2. **Переходим в рабочую директорию**
      ```
      cd megashop/
      ```
  3. **Запускаем контейнеры**
     ```bash
     docker compose -f docker-compose-dev.yml up --build -d
     ```
  4. **Мигрируем базу данных**
     ```bash
     docker compose -f docker-compose-dev.yml exec web python manage.py migrate
     ```
  5. **Создаём администратора (суперпользователя Django)**
     ```bash
     docker compose -f docker-compose-dev.yml exec web python manage.py createsuperuser
     ```
  6. **Сбор статики**
        ```bash
        docker compose exec web python manage.py collectstatic
        ```
  7. **Создаём индексы Elasticsearch**
     ```bash
     docker compose -f docker-compose-dev.yml exec web python manage.py search_index --create
     ```
  8. **Перестраиваем индексы Elasticsearch**
     ```bash
     docker compose -f docker-compose-dev.yml exec web python manage.py search_index --rebuild
     ```

- ## Важное
  - **Настроить переменные Github actions secret**
  - **ЕСЛИ ОШИБКА ДОСТУПА К ФАЙЛУ wait-for-it.sh**
    ```bash
    chmod +x wait-for-it.sh 
    ```
  - **Если ошибка доступа к кэшу ElasticSearch**

    ```bash
    sudo chown -R 1000:1000 ./data/elasticsearch
    sudo chmod -R 755 ./data/elasticsearch
    ```
    ### Таблица переменных окружения GITLAB CI/CD

    | **Переменная**    | **Описание**           |
    | ----------------- | ---------------------- |
    | `SSH_PRIVATE_KEY` | Приватный ключ         |
    | `SSH_HOST`        | Хост сервера           |
    | `SSH_USER`        | Пользователь           |
    | `GIT_USER`        | Пользователь Git       |
    | `GIT_TOKEN`       | Git token пользователя |
