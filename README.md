
# Darky Users & News Service
### Описание

Кастомный сервис для GML.Launcher предназначенный для работы с пользователями и новостями с возможностью интеграции как отдельный контейнер в docker compose лаунчера.

### Установка
Выполните команду ниже в директории вашего лаунчера
```git clone https://github.com/darkywings/Darky.UserNews.Service.git```

Должна получиться следующая структура проекта:
```
|--data
|--frontend
|--docker-compose.yml
|--.env
|--Darky.UserNews.Service
```

## Настройка
Подготовьте файл ```.env``` вручную, используя образец ```./Darky.UserNews.Service/.env.example```

Все поля можно оставить по умолчанию, но рекомендуется указать другие данные для авторизации под ролью администратора(ADMIN_LOGIN и ADMIN_PASSWORD). А также поменять JWT_SECRET_KEY на свой, чтобы больше обезопасить API от несанкционированного доступа.

### Запуск
Сервис может работать как в Docker Compose так и напрямую

#### Прямой запуск
Установите зависимости
```pip install -r requirements.txt```

Запустите скрипт ```__main__.py```
```python .``` или ```python __main__.py```

#### Запуск через Docker Compose
Впишите следующий кусок конфигурации в ваш docker-compose.yml
```
darky-users-news-api:
  container_name: darky-users-news-api
  restart: always
  build:
    context: ./Darky.UserNews.Service
    dockerfile: Dockerfile
  ports:
    - "${PORT_DARKY_API}: 8000"
  networks:
    - gml-network
  environment:
    - TZ=Europe/Moscow
  user: "${UID}:${GID}"
  volumes:
    - ./data/AuthService:/app/data
```

А также в файле ```.env``` вашего лаунчера пропишите желаемый порт на котором будет работать ваш сервис
```PORT_DARKY_API=8004```

Теперь при запуске серверной части лаунчера у вас будет подниматься 4 контейнера, а не 3:
```
[+] Running 4/4
 ✔ darky-users-news-api    Started
 ✔ gml-web-api             Started
 ✔ gml-frontend            Started
 ✔ gml-web-skins           Started
```

Управлять аккаунтами и новостями можно напрямую через API Swagger сервиса по вашему ip и порту который вы указали для этого сервиса (```http://localhost:8004/docs``` например)