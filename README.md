# Cервис для публикаций и обмена рецептами.


Авторизованные пользователи могут подписываться на понравившихся авторов, добавлять рецепты в избранное, в покупки, скачивать список покупок. Неавторизованным пользователям доступна регистрация, авторизация, просмотр рецептов других пользователей.

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

## Описание проекта и функционала

### Главная страница

Содержимое главной страницы — список рецептов, отсортированных по дате публикации (от новых к старым).

### Страница рецепта

На странице — полное описание рецепта, возможность добавить рецепт в избранное и в список покупок, возможность подписаться на автора рецепта.

### Страница пользователя

На странице — имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.

### Подписка на авторов

Подписка на публикации доступна только авторизованному пользователю. Страница подписок доступна только владельцу.

### Сценарий поведения пользователя:

- Пользователь переходит на страницу другого пользователя или на страницу рецепта и подписывается на публикации автора кликом по кнопке `Подписаться на автора`.
- Пользователь переходит на страницу «Мои подписки» и просматривает список рецептов, опубликованных теми авторами, на которых он подписался. Сортировка записей — по дате публикации (от новых к старым).
- При необходимости пользователь может отказаться от подписки на автора: переходит на страницу автора или на страницу его рецепта и нажимает `Отписаться от автора`.

### Список избранного
Работа со списком избранного доступна **только авторизованному** пользователю. Список избранного может просматривать **только его владелец**.  

**Сценарий поведения пользователя:**

- Пользователь отмечает один или несколько рецептов кликом по кнопке `Добавить в избранное`.
- Пользователь переходит на страницу `«Список избранного»` и просматривает персональный список избранных рецептов.
- При необходимости пользователь может `Удалить` рецепт из избранного.

### Список покупок
Работа со списком покупок доступна **авторизованным и не авторизованным** пользователям. 
Список покупок может просматривать **только его владелец**.
**Сценарий поведения пользователя:**

- Пользователь отмечает один или несколько рецептов кликом по кнопке `Добавить в покупки`.
- Пользователь переходит на страницу `Список покупок`, там доступны все добавленные в список рецепты. Пользователь нажимает кнопку `Скачать` список и получает файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в `«Списке покупок»`.
- При необходимости пользователь может удалить рецепт из списка покупок.

Список покупок скачивается в формате PDF.
При скачивании списка покупок ингредиенты в результирующем суммируются 
`если в двух рецептах есть сахар (в одном рецепте 5 г, в другом — 10 г), то в списке будет один пункт: Сахар — 15 г.`

### Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — на странице будут показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. 
При фильтрации на странице избранного фильтруются только избранные рецепты. 


### Регистрация и авторизация
В проекте доступна система регистрации и авторизации пользователей. 
Обязательные поля для пользователя:

    Логин
    Пароль
    Email

### Что могут делать неавторизованные пользователи

- Создать аккаунт.
- Просматривать рецепты на главной.
- Просматривать отдельные страницы рецептов.
- Просматривать страницы пользователей.
- Фильтровать рецепты по тегам.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.

### Что могут делать авторизованные пользователи

- Входить в систему под своим логином и паролем.
- Выходить из системы (разлогиниваться).
- Восстанавливать свой пароль.
- Менять свой пароль.
- Создавать/редактировать/удалять собственные рецепты
- Просматривать рецепты на главной.
- Просматривать страницы пользователей.
- Просматривать отдельные страницы рецептов.
- Фильтровать рецепты по тегам.
- Работать с персональным списком избранного: добавлять/удалять чужие рецепты, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

# Подготовка к запуску и запуск проекта foodgram

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Перейти в основную папку и выполнить миграции:

```
cd foodgram
```

Выполнить миграцию:

```
python manage.py migrate
```

Заполненить базу данных CSV-файлами:

```
python manage.py uploadDB tags.csv ingredients.csv
```

Запустить проект:

```
python manage.py runserver
```

# Пример заполнения файла .env:

SECRET_KEY=ab^&91hzhl%sdfw-=u7utwqq@d=_je3q9xsur#$0h=8j4rncdwy

DEBUG=True

DB_ENGINE=django.db.backends.postgresql

DB_NAME=postgres

POSTGRES_USER=postgres

POSTGRES_PASSWORD=postgres

DB_HOST=db

DB_PORT=5432

## Стек технологий
Python 3.9.7, Django 3.2.7, Django REST Framework 3.12, PostgresQL, Docker, Yandex.Cloud.


## Команды, необходимые для работы с контейнерами и на сервере

sudo docker-compose exec web python manage.py migrate

sudo docker-compose exec web python manage.py createsuperuser

sudo docker-compose exec web python manage.py collectstatic --no-input 

sudo docker-compose exec web python manage.py uploadDB tags.csv ingredients.csv

docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser

docker-compose exec web python manage.py collectstatic --no-input 

docker-compose exec web python manage.py uploadDB tags.csv ingredients.csv

