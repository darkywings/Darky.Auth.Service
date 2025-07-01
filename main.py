from fastapi import FastAPI, HTTPException
from database import init_db
from models import add_user_to_db, sign_in_user
from schemas import UserCredentials
from dotenv import load_dotenv
import os
import uvicorn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="DarkyGMLUserService",
    lifespan=lifespan
)

load_dotenv()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

@app.post("/users/new")
async def add_user(credentials: UserCredentials):
    return add_user_to_db(credentials.login, credentials.password)

@app.post("/users/get")
async def sign_in(credentials: UserCredentials):
    return sign_in_user(credentials.login, credentials.password)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)