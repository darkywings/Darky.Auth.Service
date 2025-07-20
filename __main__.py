import os
from fastapi import FastAPI, APIRouter, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

from users_service.users import Users
from news_service.news import News

if not os.path.exists("data"):
    os.mkdir("data")

app = FastAPI(
    title=os.getenv("API_NAME", "DARKY User & News Service"),
    description="Custom User and News API",
    version=os.getenv("API_VERSION", "0.0.1")
)

users = Users(os.getenv("API_SECURITY_KEY"))
news = News(os.getenv("API_SECURITY_KEY"))

app.include_router(users.router)
app.include_router(news.router)

@app.get("/ping", tags=["System"], name="Ping the service", description="Pinging the API, should return Pong OwO!")
async def ping():
    return {"Message": "Pong OwO!"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)