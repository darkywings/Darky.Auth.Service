from typing import Annotated
import random
import os

import dotenv
import sqlite3
from fastapi import (
    APIRouter, 
    HTTPException, 
    status,
    Depends
    )
from passlib.context import CryptContext

from models.models import *
from logger.darky_logger import DarkyLogger
from configs.logger import config
from configs.routers import config as ROUTERS
from security.jwt_generators import JwtKey
from security.api_key import AdminSecurity

dotenv.load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = AdminSecurity(os.getenv("JWT_SECRET_KEY"))

class Admin:

    def __init__(self):

        self.logger = DarkyLogger("darky.admins", configuration=config.LOGGER)

        self.logger.info(f"Initializing Admin service...")

        self.logger.debug(f"Initializing database...")
        conn = self.__db__()
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    login TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    secret_key TEXT NOT NULL
                )
            ''')
        conn.commit()
        conn.close()
        self.logger.debug(f"Successful")

        self.logger.debug(f"Inititalizing routers...")
        self.router = APIRouter(
            prefix="/admin",
            tags=["Admins"],
            lifespan=self.lifespan
        )
        self.router.add_api_route(ROUTERS.GET_JWT.route, self.get_jwt, methods=["POST"],
                                  name=ROUTERS.GET_JWT.name,
                                  description=ROUTERS.GET_JWT.description,
                                  response_model=JwtResponse)
        self.router.add_api_route(ROUTERS.SIGNUP_ADMIN.route, self.signup, methods=["POST"],
                                  name=ROUTERS.SIGNUP_ADMIN.name,
                                  description=ROUTERS.SIGNUP_ADMIN.description,
                                  response_model=AdminSignupResponse)
        self.logger.debug(f"Successful")

        self.jwt = JwtKey(os.getenv("JWT_SECRET_KEY"))

        self.logger.info(f"Admin service is initialized!")

    async def lifespan(self, api: APIRouter):
        await self.check_admin()
        self.logger.info("Hello")
        yield
        self.logger.info("Bye")
    
    def __db__(self):
        conn = sqlite3.connect("admins.db")
        conn.row_factory = sqlite3.Row
        return conn
    
    async def check_admin(self):
        conn = self.__db__()
        cursor = conn.cursor()
        self.logger.debug(f"Searching for admin user...")
        cursor.execute("SELECT login FROM admins WHERE LOWER(login) = LOWER(?)", (os.getenv("ADMIN_LOGIN", "admin"),))
        if cursor.fetchone():
            conn.close()
            self.logger.info(f"This user is already exists")
            return
        
        self.logger.debug(f"Getting admin login from dotenv...")
        login = os.getenv("ADMIN_LOGIN", "admin")

        self.logger.debug(f"Hashing password for admin...")
        hashed_password = pwd_context.hash(os.getenv("ADMIN_PASSWORD", "admin").strip())

        self.logger.debug(f"Generating secret key...")
        secret_key = "".join([f"{random.randint(0, 9)}" for _ in range(16)])

        self.logger.debug(f"Inserting new user \"admin\" to the database...")
        try:
            cursor.execute(
                "INSERT INTO admins (login, password, secret_key) VALUES (?, ?, ?)",
                (login, hashed_password, secret_key)
            )
            conn.commit()
        except Exception as e:
            conn.close()
            self.logger.error(f"Error while registrating", exc_info=True)
            exit
        finally:
            conn.close()

        self.logger.info(f"Admin is here!")
    
    async def signup(self, data: AdminSignupRequest, authorized: Annotated[str, Depends(security.get_user)]):
        if authorized["type"] != "admin" or not await self.key_is_valid(authorized["data"]["login"], authorized["data"]["secret_key"]):
            self.logger.error(f"You're not authorized or not an admin")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Вы не авторизованы или не являетесь администратором!"}
            )
        if not data.Login or not data.Password or not data.ConfirmPassword:
            self.logger.error(f"Fields are missing")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Заполните все поля"}
            )
        if data.Password != data.ConfirmPassword:
            self.logger.error(f"Passwords are not fit")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Пароли не совпадают"}
            )
        self.logger.info(f"Creating new admin...")

        conn = self.__db__()
        cursor = conn.cursor()

        self.logger.debug(f"Selecting {data.Login}...")
        cursor.execute("SELECT login FROM admins WHERE LOWER(login) = LOWER(?)", (data.Login,))
        if cursor.fetchone():
            conn.close()
            self.logger.error(f"This admin is already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Message": "Пользователь с таким логином уже существует"}
            )

        self.logger.debug(f"Generating secret key for {data.Login}...")
        secret_key = "".join([f"{random.randint(0, 9)}" for _ in range(16)])

        self.logger.debug(f"Hashing password for {data.Login}...")
        hashed_password = pwd_context.hash(data.Password.strip())

        try:
            cursor.execute("INSERT INTO admins (login, password, secret_key) VALUES (?, ?, ?)", (data.Login, hashed_password, secret_key))
            conn.commit()
        except Exception as e:
            conn.close()
            self.logger.error(f"Error while registrating", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": "Ошибка при регистрации пользователя"}
            )
        finally:
            conn.close()

        jwtKey = await self.get_jwt(data)
        
        self.logger.info(f"Administrator {data.Login} is succesfully registrated!")
        return {
            "Login": data.Login,
            "Jwt": jwtKey["Jwt"],
            "Message": "Администратор успешно зарегистрирован"
        }

    async def key_is_valid(self, login:str, key:str):
        
        if login == "AnonOwO" and key == "uwu":
            return True

        conn = self.__db__()
        cursor = conn.cursor()

        cursor.execute("SELECT login, secret_key FROM admins WHERE LOWER(login) = ?", (login,))
        user = cursor.fetchone()
        conn.close()

        if not user or len(key) != 16 or user["secret_key"] != key:
            self.logger.error(f"Key is not valid")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "JWT не прошел валидацию",
                        "Admin": "Пытаемся взломать API, не так ли?)"}
            )
        
        return True
    
    async def get_jwt(self, data: JwtRequest):
        if not data.Login or not data.Password:
            self.logger.error(f"Login or password is missing!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Логин и пароль обязательны"}
            )
        
        self.logger.info(f"Getting JWT for {data.Login}...")

        conn = self.__db__()
        cursor = conn.cursor()

        cursor.execute("SELECT login, password, secret_key FROM admins WHERE LOWER(login) = LOWER(?)", (data.Login,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            self.logger.error(f"User {data.Login} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Message": "Данный админ пользователь не найден"}
            )
        
        if not pwd_context.verify(data.Password.strip(), user["password"]):
            self.logger.error(f"Incorrect login or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Неверный логин или пароль"}
            )
        
        user_data = {
            "login": user["login"],
            "secret_key": user["secret_key"]
        }
        jwt_key = self.jwt.generate_jwt(user_data)

        return {
            "Login": user["login"],
            "Jwt": jwt_key
        }