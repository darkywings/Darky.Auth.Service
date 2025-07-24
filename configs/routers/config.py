class PING:
    name="Пинг API"
    description="Пингует API. В ответ должен вернуть Pong OwO"
    tags=["System"]
    route="/ping"

class WHOAMI:
    name="Проверить данные по JWT"
    description="Декодирует JWT и выдает информацию о авторизованном в API пользователе(администраторе)"
    tags=["System"]
    route="/whoami"

class SIGNUP_ADMIN:
    name="Добавить администратора"
    description="Добавляет новый администратоский аккаунт с собственным JWT ключем"
    route="/signup"

class GET_JWT:
    name="Получить JWT"
    description="Выдает JWT указанного аккаунта для авторизации в API и получения доступа к некоторым функциям"
    route="/getJwt"