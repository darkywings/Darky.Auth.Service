from pydantic import BaseModel

class UserCredentials(BaseModel):
    Login: str
    Password: str