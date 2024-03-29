![example workflow](https://github.com/GenVas/yamdb_final/actions/workflows/main.yml/badge.svg)

# Запуск сервиса API YaMDB на сервере через Docker
## Проект запущен на сервере и доступен по адресу: http://84.201.175.214/redoc/

Это тестовый проект Django для запуска API через Docker.

В качестве основы использован проект [GenVas/api_yamdb]: https://github.com/GenVas/api_yamdb.git
Проект YaMDbet собирает отзывы пользователей о различных произведениях искусства.
Произведения поделены на такие категории, как «Книги», «Фильмы», «Музыка».
Список категорий может быть расширен администратором.
Сами произведения не храняться в YaMDb, здесь нельзя смотреть фильмы или слушать музыку.
Произведение может иметь жанровый класс из списка предустановленных.
(например, «Сказка», «Скала» или «Артхаус»). Новые жанры могут быть созданы только администратором.

## Возможнности

- Создавать, удалять, редактировать пользователя (может как администратор так и владелец профиля пользователя);
- Выбирать уникальный жанр для произведения искусства;
- Создавать и публиковать свои обзоры о разных произведениях;
- Оставить комментарий к обзору или прокоментировать комментарий;
- Просмотр других отзывов со всеми комментариями.


## Установка приложения

- Клонировать и перейти в репозиторий с помощью терминала:

   ```sh
   git clone https://github.com/GenVas/yamdb_final
   ```

   ```sh
   cd yamdb_final
   ```

- Создать виртуальную среду

   ```sh
   ls
   ```

## Запуск с помощью Docker

   Проект рассчитан на запуск c помощью Docker и Docker-Compose

1. Установите docker и docker-compose

   Инструкция по установке доступна в официальной документации [https://www.docker.com/get-started]

   Образ проект загружен в Docker Hub [geedeega/yamdb:v1.11]
   ```sh
   docker push geedeega/yamdb:v1.1
   ```
2. Сформируйте .env файл со следующими переменными:

   ```sh
   SECRET_KEY=p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs
   DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
   DB_NAME=postgres # имя базы данных
   POSTGRES_USER=postgres # логин для подключения к базе данных
   POSTGRES_PASSWORD=postgres # пароль для подключения к БД
   DB_HOST=db # название сервиса (контейнера)
   DB_PORT=5432 # порт для подключения к БД
   EMAIL_FILE_PATH='/code/sent_emails/'
   ```

3. Запустите контенеры

   ```sh
   docker-compose up
   ```

4. Выполните миграции и создайте суперпользователя
   
   ```sh
   docker-compose exec web python manage.py migrate --noinput
   ```

   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```
   введите учетные данные: логин, электронную почту и пароль

5. Соберите статистику:

   ```sh
   docker-compose exec web python manage.py collectstatic --noinput
   ```

6. Выгрузите фикстуры:

   В корневой папке проекта лежит тестовая база данных. для ее загрузки используйте следующую команду:

   ```sh
   docker-compose exec web python manage.py loaddata fixtures.json
   ```

   Более подробная информация о загрузке данных: https://docs.djangoproject.com/en/3.2/howto/initial-data/

7. Для работы с базой в режиме разработки черех запросы API вам потребуется получить токен. Важно отметить, что для получения токена вам потребуется ввод confirmation code, который будет сохранен в папке  sent_emails/ контейнера.

   Для доступа к содержимому контейнера для проверки папки sent_emails/  пользуйтесь командой

   ```sh
   docker exec -it <номер контейнера> bash
   ```

## Работа с проектов на удаленном сервере

Сразу после клонирования проекта сделайте следующее:

- Установите Docker и Docker-compose. Эта команда скачает скрипт для установки докера:

   Инструкция по установке доступна в официальной документации [https://www.docker.com/get-started]

- скопируйте Docker-compose.yaml файл на сервер, например, c помошью scp
- скорпируйте папку nginx/ с конфигурацией сервера nginx в ту же директорию, где назодится файл Docker-compose

- добавьте в Secrets в разделе Actions репозитария своего проекта в разделе настройки следующие
secrets:

   Доступ к Docker:
      DOCKER_USERNAME
      DOCKER_PASSWORD
   Доступ к вашему серверу:
      HOST - IP server
	   USER - имя пользователя
	   PASSPHRASE пароль, если есть
	   SSH_KEY: ключ для доступа
   Cекретный ключ джанго:
      SECRET_KEY 
   Параметры базы данных Postgres:
      DB_ENGINE
      DB_NAME
      POSTGRES_USER
      POSTGRES_PASSWORD
      DB_HOST
      DB_PORT
   Телеграм:
      TELEGRAM_TO: ID аккаунта для получения сообщений
	   TELEGRAM_TOKEN: токен вашего бота для отправки сообщений

- перед отправкой кода на сервер проверьте, не занят ли порт nginx. Принеобходимости, остановите Nginx

   ```sh
   sudo systemctl stop nginx
   ```

## Тип лицензии

   MIT

   [Django 2.2.6]: <https://www.djangoproject.com/download/>
   [Python 3.7]: <https://www.python.org/downloads/release/python-390/>
   [Docker 20.10.8]: https://www.docker.com/
   [Nginx 1.19.3]: https://nginx.org/
   [GenVas/api_yamdb]: https://github.com/GenVas/api_yamdb.git 
   [postgres:12.4-alpine] https://hub.docker.com/r/onjin/alpine-postgres/
   [nginx:1.19.3-alpine] https://hub.docker.com/layers/nginx/library/nginx/1.19.3-alpine/images/sha256-4e21f77cde9aaeb846dc799b934a42b66939d19755d98829b705270e916c7479?context=explore 
   [GitHub Actions] https://docs.github.com/en/actions
   
