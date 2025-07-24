from pydantic import BaseModel
from typing import Optional


class JwtRequest(BaseModel):
    Login: str
    Password: str

class AdminSignupRequest(JwtRequest):
    ConfirmPassword: str

class JwtResponse(BaseModel):
    Login: str
    Jwt: str

class WhoAmIResponse(BaseModel):
    Type: str
    Since: str
    Login: str
    IsValid: bool

class AdminSignupResponse(JwtResponse):
    Message: str



class EditUuidRequest(BaseModel):
    Login: str
    NewUuid: str

class UserRequest(BaseModel):
    Login: str

class UserAuthRequest(UserRequest):
    Password: str

class UserDeleteRequest(UserRequest):
    pass


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
    pass

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
    id: Optional[int] = None
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
