# Мегамагазин на Django
## CI CD
https://gist.github.com/s-lyn/81767ed6c67138eaba681d7739a9db61
# Пошаговый деплой
1. ```git clone https://gitlab.altawest.ru/products/shop-backend```
2. ```cd megashop/```
3. ```sudo apt install certbot python3-certbot-nginx```
4. ```sudo certbot certonly --nginx -d <ВСТАВИТЬ URL> --config-dir ssl/```
5. ```docker compose up -d --build```
6. ```docker compose exec web python manage.py migrate```
7. ```docker compose exec web python manage.py createsuperuser```
# Запуск окружения разработчика
1. ```git clone https://gitlab.altawest.ru/products/shop-backend```
2. ```cd megashop/```
3. ```docker compose -f docker-compose-dev.yml up```
Открываем новый терминал
4. ```docker compose -f docker-compose-dev.yml exec web python manage.py migrate```
5. ```docker compose -f docker-compose-dev.yml exec web python manage.py createsuperuser```
## Важное
- Настроить переменные Github actions secret
- ЕСЛИ ОШИБКА ДОСТУПА К ФАЙЛУ wait-for-it.sh
```
chmod +x wait-for-it.sh 
```
- Получение сертификата
```
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d <ВСТАВИТЬ URL> --config-dir ssl/
```
- Переменные GITHUB_ACTIONS
``` 
SSH_PRIVATE_KEY - приватный ключ
SSH_HOST - хост сервера
SSH_USER - пользователь
GIT_USER - пользователь Git
GIT_TOKEN - git token пользователя
```
- Миграция бд sqlite -> postgresql
```
./manage.py dumpdata --exclude auth.permission --exclude contenttypes > db.json
./manage.py loaddata db.json
```
- Сбор статики
```
docker compose exec web python manage.py collectstatic --settings=megashop.settings.prod
```
## RELEASE NOTES
### Версия 1.1.1 (19.01.2024)

**Добавлено:**
- Инициализация системы
- Базовые CRUD API

**Исправлено:**
- 