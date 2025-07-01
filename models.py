import sqlite3
import uuid
from fastapi import HTTPException
from database import get_db_connection

def add_user_to_db(login: str, password: str):
    if not login.strip() or not password.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "StatusCode": 400,
                "Message": "Пустой логин или пароль",
                "Details": "Логин и пароль не могут быть пустыми"
            }
        )
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            user_uuid = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (login, password) VALUES (?, ?)",
                (login, password)
            )
            conn.commit()
            return {
                "Response": {"login": login, "password": password},
                "StatusCode": 200,
                "Message": "Пользователь успешно добавлен"
            }
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=400,
                detail={
                    "StatusCode": 400,
                    "Message": "Такой пользователь уже есть",
                    "Details": "Пользователь с таким логином уже существует"
                }
            )

def sign_in_user(login: str, password: str):
    if not login.strip() or not password.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "StatusCode": 400,
                "Message": "Пустой логин или пароль",
                "Details": "Логин и пароль не могут быть пустыми"
            }
        )
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT login, password FROM users WHERE login = ?",
            (login)
        )
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "StatusCode": 404,
                    "Message": "Пользователь не найден",
                    "Details": "Пользователь с указанным логином не существует"
                }
            )
        
        db_login, db_password = user
        
        if db_password != password:
            raise HTTPException(
                status_code=401,
                detail={
                    "StatusCode": 401,
                    "Message": "Неверный логин или пароль",
                    "Details": "Указанный пароль не соответствует"
                }
            )
        
        return {
            "Login": login,
            "StatusCode": 200,
            "Message": "Успешная авторизация"
        }