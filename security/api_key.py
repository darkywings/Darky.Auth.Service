from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
import jwt

security_scheme = HTTPBearer(
    scheme_name="JWT Token",
    description="Вставьте JWT администратора для авторизации под его ролью. В случае если вам не известен JWT воспользуйтесь методом getJwt",
    auto_error=False
)

class AdminSecurity:

    def __init__(self, jwt_secret: str):
        self.__jwt_secret__ = jwt_secret

    def decode(self, credentials: Annotated[str | None, Depends(security_scheme)]):
        
        if not credentials:
            return {"type": "anon_owo",
                    "date": "owo",
                    "data": {
                        "login": "AnonOwO",
                        "secret_key": "uwu"
                    }}

        token = credentials.credentials
        try:
            decoded_jwt = jwt.decode(token, self.__jwt_secret__, algorithms=["HS256"])
            return decoded_jwt
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"Message": "Доступ запрещен: Неверный или истекший токен"}
            )

    def get_user(self, credentials: Annotated[str | None, Depends(security_scheme)]):
        return self.decode(credentials)