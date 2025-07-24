import os
from fastapi import FastAPI, APIRouter, HTTPException, status, Depends
from dotenv import load_dotenv
from typing import Annotated, Optional

load_dotenv()

from users_service.users import Users
from news_service.news import News

from models.models import *
from security.api_key import AdminSecurity
from security.admin import Admin

from configs.routers import config as CONFIG

if not os.path.exists("data"):
    os.mkdir("data")

app = FastAPI(
    title=os.getenv("API_NAME", "DARKY User & News Service"),
    description="Custom User and News API",
    version=os.getenv("API_VERSION", "0.0.1")
)

admin = Admin()
users = Users(admin)
news = News(admin)

security = AdminSecurity(os.getenv("JWT_SECRET_KEY"))

app.include_router(users.router)
app.include_router(news.router)
app.include_router(admin.router)

@app.get(path=CONFIG.PING.route, 
         tags=CONFIG.PING.tags, 
         name=CONFIG.PING.name, 
         description=CONFIG.PING.description)
async def ping():
    return {"Message": "Pong OwO!"}

@app.get(path=CONFIG.WHOAMI.route,
         tags=CONFIG.WHOAMI.tags,
         name=CONFIG.WHOAMI.name,
         description=CONFIG.WHOAMI.description)
async def whoami(current_user: Annotated[str, Depends(security.get_user)]):
    keyValid = await admin.key_is_valid(current_user["data"]["login"], current_user["data"]["secret_key"])
    if keyValid:
        return {
            "Type": current_user["type"],
            "Since": current_user["date"],
            "Login": current_user["data"]["login"],
            "IsValid": keyValid
        }
    return {
        "IsValid": keyValid
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)