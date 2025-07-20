import sqlite3
from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
import uuid

from models.models import *

from logger.darky_logger import DarkyLogger
from logger import config

# Конфигурация для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Users:


    def __init__(self,
                 security_key):
        self.logger = DarkyLogger("darky.users", configuration=config.LOGGER)

        self.logger.info(f"Initializing Users service...")

        self.logger.debug(f"Initializing database...")
        conn = self.__db__()
        cursor = conn.cursor()
        cursor.execute('''
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
        self.logger.debug(f"Successful")

        self.logger.debug(f"Inititalizing routers...")
        self.router = APIRouter(
            prefix="/users",
            tags=["Users"]
        )
        self.router.add_api_route("/auth", self.auth_user, methods=["POST"],
                                  name="Auth User",
                                  description="Authorizing user from database data",
                                  response_model=UserAuthResponse)
        self.router.add_api_route("/register", self.register_user, methods=["POST"],
                                  name="Registrate User",
                                  description="Registrating user in the database",
                                  response_model=UserRegisterResponse)
        self.router.add_api_route("/delete", self.delete_user, methods=["DELETE"],
                                  name="Delete User",
                                  description="Deleting user from database data",
                                  response_model=UserDeleteResponse)
        self.router.add_api_route("/edit_uuid", self.edit_uuid, methods=["POST"],
                                  name="Edit User Uuid",
                                  description="Editing user's uuid on custom one",
                                  response_model=EditUuidResponse)
        self.router.add_api_route("/get_all", self.get_users, methods=["GET"],
                                  name="Get Users",
                                  description="Getting all existing users in database",
                                  response_model=UserListResponse)
        self.logger.debug(f"Successful")

        self.__security_key__ = security_key

        self.logger.info(f"Users service is initialized!")



    def __db__(self):
        conn = sqlite3.connect("data/data.db")
        conn.row_factory = sqlite3.Row
        return conn
    


    async def auth_user(self, data: UserAuthRequest):
        
        if not data.Login or not data.Password:
            self.logger.error("Login and password are required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Логин и пароль обязательны"}
            )
        self.logger.info(f"Authorizing user {data.Login}...")

        self.logger.debug(f"Accessing to the database and selecting user...")
        conn = self.__db__()
        cursor = conn.cursor()
        cursor.execute("SELECT uuid, login, password, is_blocked, block_reason FROM users WHERE LOWER(login) = LOWER(?)", (data.Login,))
        user = cursor.fetchone()
        conn.close()
        self.logger.debug(f"Success")

        if not user:
            self.logger.error(f"User {data.Login} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Message": "Пользователь не найден"}
            )

        if user["is_blocked"]:
            self.logger.error(f"User {data.Login} is banned. Reason: {user['block_reason'] or 'Не указана'}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"Message": f"Пользователь заблокирован. Причина: {user['block_reason'] or 'Не указана'}"}
            )

        if not pwd_context.verify(data.Password.strip(), user["password"]):
            self.logger.error(f"Incorrect login or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Неверный логин или пароль"}
            )

        self.logger.info(f"User {data.Login} successfully authorized!")
        return {
            "Login": user["login"],
            "UserUuid": user["uuid"],
            "Message": "Успешная авторизация"
        }
    


    async def register_user(self, data: UserAuthRequest):

        if not data.Login or not data.Password:
            self.logger.error(f"Login and password are required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Логин и пароль обязательны"}
            )
        self.logger.info(f"Registrating user {data.Login}...")

        self.logger.debug(f"Accesssing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()

        self.logger.debug(f"Selecting {data.Login}...")
        cursor.execute("SELECT login FROM users WHERE LOWER(login) = LOWER(?)", (data.Login,))
        if cursor.fetchone():
            conn.close()
            self.logger.error(f"This user is already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Message": "Пользователь с таким логином уже существует"}
            )

        self.logger.debug(f"Generating UUID for {data.Login}...")
        user_uuid = str(uuid.uuid4())
        self.logger.debug(f"Hashing password for {data.Login}...")
        hashed_password = pwd_context.hash(data.Password.strip())

        self.logger.debug(f"Inserting new user \"{data.Login}\" to the database...")
        try:
            cursor.execute(
                "INSERT INTO users (uuid, login, password) VALUES (?, ?, ?)",
                (user_uuid, data.Login, hashed_password)
            )
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

        self.logger.info(f"User {data.Login} is succesfully registrated!")
        return {
            "Login": data.Login,
            "Password": data.Password,
            "Message": "Пользователь успешно зарегистрирован"
        }
    


    async def delete_user(self, data: UserDeleteRequest):

        if not data.Login:
            self.logger.error(f"Login is required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Логин обязателен"}
            )
        if not data.AccessToken:
            self.logger.error(f"AccessToken is required!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Ключ доступа не указан"}
            )
        if data.AccessToken != self.__security_key__:
            self.logger.error(f"Invalid AccessToken!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Доступ запрещен: Неправильный ключ доступа"}
            )
        self.logger.info(f"Deleting user {data.Login}...")
        
        self.logger.debug(f"Accessing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()
        self.logger.debug(f"Selecting {data.Login} in database...")
        cursor.execute("SELECT uuid, login FROM users WHERE LOWER(login) = LOWER(?)", (data.Login,))
        existing_user = cursor.fetchone()

        if not existing_user:
            conn.close()
            self.logger.error(f"User {data.Login} not found!")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Message": "Пользователь не найден"}
            )
        
        self.logger.debug(f"Deleting {data.Login} from database...")
        try:
            cursor.execute("DELETE FROM users WHERE LOWER(login) = LOWER(?)", (data.Login,))
            conn.commit()
            
            if cursor.rowcount == 0:
                conn.close()
                self.logger.error(f"Error while deleting", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"Message": "Ошибка при удалении пользователя"}
                )
                
            conn.close()
            self.logger.info(f"User {data.Login} succesfully deleted!")
            return {"Message": "Пользователь успешно удален"}
            
        except Exception as e:
            conn.close()
            self.logger.error(f"Error while deleting", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": f"Ошибка при удалении пользователя: {str(e)}"}
            )
        


    async def edit_uuid(self, data: EditUuidRequest):

        if not data.AccessToken:
            self.logger.error(f"AccessToken is required!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Требуется ключ доступа"}
            )
        if data.AccessToken != self.__security_key__:
            self.logger.error(f"Invalid AccessToken")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Доступ запрещен: Неправильный ключ доступа"}
            )
        
        if not data.Login:
            self.logger.error(f"Login is required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Логин обязателен"}
            )
        
        self.logger.info(f"Editing user uuid manually {data.Login}...")

        self.logger.debug(f"Accessing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()
        self.logger.debug(f"Selecting {data.Login} in database...")
        cursor.execute("SELECT uuid, login FROM users WHERE LOWER(login) = LOWER(?)", (data.Login,))
        user = cursor.fetchone()

        if not user:
            self.logger.error(f"User {data.Login} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Message": "Пользователь не найден"}
            )
        
        if not hasattr(data, 'NewUuid') or not data.NewUuid:
            self.logger.error(f"New UUID is required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Новый UUID обязателен"}
            )
        
        self.logger.debug(f"Setting new UUID for {data.Login}...")
        new_uuid = str(data.NewUuid)

        self.logger.debug(f"Updating UUID for user {data.Login} in database...")
        try:
            cursor.execute(
                "UPDATE users SET uuid = ? WHERE LOWER(login) = LOWER(?)",
                (new_uuid, data.Login)
            )
            conn.commit()
            if cursor.rowcount == 0:
                self.logger.error(f"Failed to update UUID for user {data.Login}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"Message": "Ошибка при обновлении UUID"}
                )
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error while updating UUID", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": f"Ошибка при обновлении UUID: {str(e)}"}
            )
        finally:
            conn.close()

        self.logger.info(f"UUID for user {data.Login} successfully updated to {new_uuid}")
        return {
            "Login": data.Login,
            "OldUuid": user["uuid"],
            "NewUuid": new_uuid,
            "Message": "UUID пользователя успешно обновлен"
        }
        


    async def get_users(self, accessToken:str):
        
        self.logger.info(f"Getting user list...")
        if not accessToken:
            self.logger.error(f"AccessToken is required!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Требуется ключ доступа"}
            )
        if accessToken != self.__security_key__:
            self.logger.error(f"Invalid AccessToken")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Доступ запрещен: Неправильный ключ доступа"}
            )
        
        self.logger.debug(f"Accessing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()

        self.logger.debug(f"Preparing user list...")
        try:
            cursor.execute("SELECT login, uuid FROM users ORDER BY login")
            users = cursor.fetchall()
            
            logins = [f"{user["login"]}: {user["uuid"]}" for user in users]
            
            conn.close()
            
            if not logins:
                self.logger.info(f"User list is empty")
                return {
                    "Logins": [],
                    "Message": "Список пользователей пуст"
                }
                
            self.logger.info(f"User list is ready. Total: {len(logins)} users")
            return {
                "Logins": logins,
                "Message": f"Найдено {len(logins)} пользователей"
            }
            
        except Exception as e:
            conn.close()
            self.logger.error(f"Error with getting user list", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": f"Ошибка при получении списка пользователей: {str(e)}"}
            )