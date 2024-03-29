# Продуктовый помошник: Foodgram (foodgram-project-react)

## Описание
«Продуктовый помощник» (Проект Яндекс.Практикум) Сайт является - базой кулинарных рецептов. На сайте любой пользователь может создавать свои рецепты, читать рецепты других пользователей, подписываться на других авторов, добавлять понравившиеся рецепты в избранное, составлять список покупок и скачать сформерованый список покупок в формате txt.

## Kак запустить
### Kлонируем проект:

git clone git@github.com:Mamrenko-Alex/foodgram-project-react.git
Для добавления файла .env с настройками базы данных на сервер необходимо:

### Установить соединение с сервером по протоколу ssh:

ssh username@xxx.xxx.xxx.xxx

Где:
username - имя пользователя, под которым будет выполнено подключение к серверу.
xxx.xxx.xxx.xxx - IP-адрес сервера на котором будет разворачиваться проект.

Например:

ssh mamrenko@51.250.108.235

## Docker инструкции
- После подключения к серверу необходимо установить Docker и docker-compose. После этого можно скачивать актуальные контейнеры

```
docker pull mamrenkodev/foodgram-backend:latest
docker pull mamrenkodev/foodgram-frontend:latest
```

- Файлы из папки infra переместить в корневую директорию сервера и создать файл .env

```
sudo nano .env
```

- После будет открыт редактор файлов, необходимо его заполнить следуя инструкциям ниже. DB_ENGINE; DB_HOST; DB_PORT - не меняем

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=название базы данных
POSTGRES_USER=логин суперюзера
POSTGRES_PASSWORD=пароль суперюзера
DB_HOST=db 
DB_PORT=5432
```

Проект можно развернуть используя контейнеризацию с помощью Docker  
Параметры запуска описаны в `docker-compose.yml`. Вы можете изменить их при необходимости

```
sudo docker-compose up -d
```

После запуске создаются три контейнера:

 - контейнер базы данных **db**
 - контейнер приложения **backend**
  - контейнер визуальной части **frontend**
 - контейнер web-сервера **nginx**

## Сайт доступен по адресу : http://51.250.108.235/
