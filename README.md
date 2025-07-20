# About

Кастомный сервис авторизации и регистрации пользователей для Gml.Launcher, а также кастомный сервис новостей
Работает как интеграция с лаунчером GML в виде отдельного API
Поддерживает работу через Docker Compose

## Установка
```git clone https://github.com/darkywings/Darky.UsersNews.Service.git```

## Настройка
Создайте копию .env.example, переименуйте в .env и в содержимом укажите IP и PORT на котором будет работать API этого сервиса, а также желаемое название, номер версии API и ключ доступа к этому API(не давайте его рандомным людям, с его помощью можно управлять пользователями и новостями)

## Запуск
Сервис может работать как в докере так и напрямую
Для прямого запуска просто запустите код __main__.py командой
```python __main__.py```

Для запуска из под Docker Compose встройте его в свой docker-compose.yml вставив следующий кусочек туда
```
darky-users-news-api
  container_name: darky-users-news-api
  restart: always
  build:
    context: ./Darky.UsersNews.Service
    dockerfile: Dockerfile
  ports:
    - "${PORT_DARKY}: 8000"
  networks:
    - gml-network
  environment:
    - TZ=Europe/Moscow
  user: "${UID}:${GID}"
  volumes:
    - ./data/AuthService:/app/data
```
А также вставьте в .env файл строку ```PORT_DARKY=ЗДЕСЬ ЖЕЛАЕМЫЙ ПОРТ```
Например:
```PORT_DARKY=8004```