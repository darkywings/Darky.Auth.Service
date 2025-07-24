import os
from typing import Annotated

import sqlite3
import dotenv
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends

from models.models import *
from logger.darky_logger import DarkyLogger
from configs.logger import config
from security.admin import AdminSecurity

dotenv.load_dotenv()
security = AdminSecurity(os.getenv("JWT_SECRET_KEY"))

class News:

    def __init__(self,
                 admin):
        self.logger = DarkyLogger("darky.news", configuration=config.LOGGER)

        self.logger.info(f"Initializing News service...")

        self.logger.debug(f"Initializing database...")
        conn = self.__db__()
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    date TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL
                )
            ''')
        conn.commit()
        conn.close()
        self.logger.debug(f"Successful")

        self.logger.debug(f"Inititalizing routers...")
        self.router = APIRouter(
            prefix="/news",
            tags=["News"],
            lifespan=self.lifespan
        )
        self.router.add_api_route("/add", self.add_post, methods=["POST"],
                                  name="Add new post",
                                  description="Adding new post to the News service",
                                  response_model=NewsEditResponse)
        self.router.add_api_route("/delete", self.delete_post, methods=["DELETE"],
                                  name="Delete the post",
                                  description="Deleting the post from the News service",
                                  response_model=NewsEditResponse)
        self.router.add_api_route("/get", self.get_posts, methods=["GET"],
                                  name="Get all news",
                                  description="Getting all news posts",
                                  response_model=NewsListResponse)
        self.router.add_api_route("/edit", self.edit_post, methods=["POST"],
                                  name="Edit the post",
                                  description="Editing the post's content from the News service",
                                  response_model=NewsEditedResponse)
        self.logger.debug(f"Successful")

        self.admin = admin

        self.logger.info(f"News service is initialized!")
    

    async def lifespan(self, api: APIRouter):
        await self.correct_database()
        self.logger.info("Hello")
        yield
        self.logger.info("Bye")


    def __db__(self):
        conn = sqlite3.connect("data/data.db")
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    async def get_timestamp():
        current_time = datetime.now()
        msec = current_time.microsecond // 1000
        tz="+03:00"
        return f"{current_time.strftime('%Y-%m-%dT%H:%M:%S')}.{msec}{tz}"
    
    @staticmethod
    async def get_listener():
        return "Custom"
    

    async def correct_database(self):

        self.logger.info("Correcting database...")
        
        conn = self.__db__()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, date, type FROM news")
            posts = cursor.fetchall()

            for post in posts:
                post_id = post["id"]
                new_date = post["date"].replace("Z", "+03:00")
                new_type = await self.get_listener()
                    
                cursor.execute(
                    "UPDATE news SET date = ?, type = ? WHERE id = ?",
                    (new_date, new_type, post_id)
                )
                self.logger.debug(f"Updated post ID:{post_id} - date: {new_date}, type: {new_type}")
                
            conn.commit()
            self.logger.info("Database correction completed successfully")
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error during database correction: {str(e)}", exc_info=True)
            raise Exception("Failed to correct database")
            
        finally:
            conn.close()
    

    async def add_post(self, data: NewsAddRequest, authorized: Annotated[str, Depends(security.get_user)]):
        if authorized["type"] != "admin" or not await self.admin.key_is_valid(authorized["data"]["login"], authorized["data"]["secret_key"]):
            self.logger.error(f"You're not authorized or not an admin")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Вы не авторизованы или не являетесь администратором!"}
            )
        if not data.Title or not data.Content:
            self.logger.error(f"Content required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Необходимо указать заголовок и сам контент для нового поста"}
            )
        self.logger.info(f"Adding new post {data.Title}...")
        
        self.logger.debug(f"Accesssing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()
        
        self.logger.debug(f"Inserting new post to the database...")
        try:
            cursor.execute(
                "INSERT INTO news (title, content, date, type) VALUES (?, ?, ?, ?)",
                (data.Title, data.Content, await self.get_timestamp(), await self.get_listener())
            )
            conn.commit()
            post_id = cursor.lastrowid
        except Exception as e:
            conn.close()
            self.logger.error(f"Error while posting", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": "Ошибка при добавлении поста"}
            )
        finally:
            conn.close()

        self.logger.info(f"New post was successfully added with ID: {post_id}")
        return {
            "id": post_id,
            "message": "Пост успешно добавлен"
        }

    
    async def delete_post(self, data: NewsDeleteRequest, authorized: Annotated[str, Depends(security.get_user)]):
        if authorized["type"] != "admin" or not await self.admin.key_is_valid(authorized["data"]["login"], authorized["data"]["secret_key"]):
            self.logger.error(f"You're not authorized or not an admin")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Вы не авторизованы или не являетесь администратором!"}
            )
        if not data.Id:
            self.logger.error(f"Post's ID required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Необходимо указать идентификатор поста, который необходимо удалить"}
            )
        self.logger.info(f"Deleting the post ID:{data.Id}...")

        self.logger.debug(f"Accesssing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()
        self.logger.debug(f"Selecting {data.Id} in database...")
        cursor.execute("SELECT id FROM news WHERE id = ?", (data.Id,))
        existing_post = cursor.fetchone()

        if not existing_post:
            conn.close()
            self.logger.error(f"Post {data.Id} was not found!")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Message": "Пост с указанным идентификатором не был найден"}
            )
        
        self.logger.debug(f"Deleting {data.Id} from database...")
        try:
            cursor.execute("DELETE FROM news WHERE id = ?", (data.Id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                conn.close()
                self.logger.error(f"Error while deleting", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"Message": "Ошибка при удалении поста"}
                )
                
            conn.close()
            self.logger.info(f"Post {data.Id} succesfully deleted!")
            return {
                "id": existing_post["id"],
                "message": "Пост успешно удален"
            }
            
        except Exception as e:
            conn.close()
            self.logger.error(f"Error while deleting", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": f"Ошибка при удалении поста: {str(e)}"}
            )
        
    

    async def get_posts(self):
        self.logger.info(f"Getting news list...")

        self.logger.debug(f"Accesssing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()
        self.logger.debug(f"Preparing news list...")
        try:
            cursor.execute("SELECT id, title, content, date, type FROM news ORDER BY id")
            posts = cursor.fetchall()
            
            news = [{
                "id": post["id"],
                "title": post["title"],
                "content": post["content"],
                "date": post["date"],
                "type": post["type"]
            } for post in posts]
            
            news.reverse()
                
            conn.close()
                
            self.logger.info(f"News list is ready. Total: {len(news)} posts")
            return {
                "success": True,
                "data": news
            }
            
        except Exception as e:
            conn.close()
            self.logger.error(f"Error with getting news list", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": f"Ошибка при получении новостей: {str(e)}"}
            )


    async def edit_post(self, data: NewsEditingRequest, authorized: Annotated[str, Depends(security.get_user)]):
        if authorized["type"] != "admin" or not await self.admin.key_is_valid(authorized["data"]["login"], authorized["data"]["secret_key"]):
            self.logger.error(f"You're not authorized or not an admin")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Вы не авторизованы или не являетесь администратором!"}
            )
        if not data.Id:
            self.logger.error(f"Post's ID and new content are required!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"Message": "Необходимо указать идентификатор поста, который необходимо изменить и его новое содержание"}
            )
        self.logger.info(f"Editing the post ID:{data.Id}...")

        self.logger.debug(f"Accesssing to the database...")
        conn = self.__db__()
        cursor = conn.cursor()
        self.logger.debug(f"Selecting {data.Id} in database...")
        cursor.execute("SELECT title, content FROM news WHERE id = ?", (data.Id,))
        existing_post = cursor.fetchone()

        if not existing_post:
            conn.close()
            self.logger.error(f"Post {data.Id} was not found!")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Message": "Пост с указанным идентификатором не был найден"}
            )
        
        self.logger.debug(f"Setting new content for {data.Id}...")
        new_title = f"{data.NewTitle}"
        new_content = f"{data.NewContent}"
        
        if not hasattr(data, 'NewTitle') or not data.NewTitle:
            self.logger.warning(f"Title won't be changed")
            new_title = existing_post["title"]
        
        if not hasattr(data, 'NewContent') or not data.NewContent:
            self.logger.warning(f"Content won't be changed")
            new_content = existing_post["content"]

        self.logger.debug(f"Updating content for post {data.Id} in database...")
        try:
            cursor.execute(
                "UPDATE news SET title = ?, content = ? WHERE id = ?",
                (new_title, new_content, data.Id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                self.logger.error(f"Failed to update content for post {data.Id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"Message": "Ошибка при обновлении содержимого поста"}
                )
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error while updating content for post", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"Message": f"Ошибка при обновлении содержимого поста: {str(e)}"}
            )
        finally:
            conn.close()

        self.logger.info(f"Content for post {data.Id} successfully updated!")
        return {
            "id": data.Id,
            "title": new_title,
            "content": new_content,
            "message": "Содержимое поста успешно обновлено"
        }
            