from pydantic import BaseModel
from typing import Optional


class EditUuidRequest(BaseModel):
    Login: str
    NewUuid: str
    AccessToken: str

class UserRequest(BaseModel):
    Login: str

class UserAuthRequest(UserRequest):
    Password: str

class UserDeleteRequest(UserRequest):
    AccessToken: str


class UserResponse(BaseModel):
    Message: str

class UserAuthResponse(UserResponse):
    Login: str
    UserUuid: Optional[str] = None

class UserRegisterResponse(UserResponse):
    Login: str
    Password: str

class UserDeleteResponse(UserResponse):
    pass

class UserListResponse(UserResponse):
    Logins: list[str]

class EditUuidResponse(UserResponse):
    Login: str
    OldUuid: str
    NewUuid: str
    Message: str



class NewsEditRequest(BaseModel):
    AccessToken: str

class NewsAddRequest(NewsEditRequest):
    Title: str
    Content: str

class NewsEditingRequest(NewsEditRequest):
    Id: int
    NewTitle: Optional[str] = None
    NewContent: Optional[str] = None

class NewsDeleteRequest(NewsEditRequest):
    Id: int


class NewsResponse(BaseModel):
    title: str
    content: str
    date: str
    type: str

class NewsListResponse(BaseModel):
    success: bool
    data: list[NewsResponse]

class NewsEditResponse(BaseModel):
    id: int
    message: str

class NewsEditedResponse(NewsEditResponse):
    title: str
    content: str
