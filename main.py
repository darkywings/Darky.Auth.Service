from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3
from passlib.context import CryptContext
import uuid
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Конфигурация для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модель для запросов авторизации и регистрации
class AuthRequest(BaseModel):
    Login: str
    Password: str

class AuthResponse(BaseModel):
    Login: str
    UserUuid: Optional[str] = None
    Message: str

class RegisterResponse(BaseModel):
    Login: str
    Password: str
    Message: str

# Подключение к SQLite
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uuid TEXT PRIMARY KEY,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_blocked BOOLEAN DEFAULT FALSE,
            block_reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.post("/auth", response_model=AuthResponse)
async def auth_user(auth: AuthRequest):
    if not auth.Login or not auth.Password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Message": "Логин и пароль обязательны"}
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uuid, login, password, is_blocked, block_reason FROM users WHERE LOWER(login) = LOWER(?)", (auth.Login,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Message": "Пользователь не найден"}
        )

    if user["is_blocked"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"Message": f"Пользователь заблокирован. Причина: {user['block_reason'] or 'Не указана'}"}
        )

    if not pwd_context.verify(auth.Password.strip(), user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"Message": "Неверный логин или пароль"}
        )

    return {
        "Login": user["login"],
        "UserUuid": user["uuid"],
        "Message": "Успешная авторизация"
    }

@app.post("/register", response_model=RegisterResponse)
async def register_user(auth: AuthRequest):
    if not auth.Login or not auth.Password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Message": "Логин и пароль обязательны"}
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверка на существование пользователя
    cursor.execute("SELECT login FROM users WHERE LOWER(login) = LOWER(?)", (auth.Login,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"Message": "Пользователь с таким логином уже существует"}
        )

    # Создание нового пользователя
    user_uuid = str(uuid.uuid4())
    hashed_password = pwd_context.hash(auth.Password.strip())

    try:
        cursor.execute(
            "INSERT INTO users (uuid, login, password) VALUES (?, ?, ?)",
            (user_uuid, auth.Login, hashed_password)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"Message": "Ошибка при регистрации пользователя"}
        )
    finally:
        conn.close()

    return {
        "Login": auth.Login,
        "Password": auth.Password,
        "Message": "Пользователь успешно зарегистрирован"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)