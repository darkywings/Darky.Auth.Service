import os
from dotenv import load_dotenv

import jwt
from datetime import datetime

load_dotenv()

class JwtKey:

    def __init__(self,
                 jwt_secret=os.getenv("JWT_SECRET_KEY")):
        self.jwt_secret = jwt_secret
    
    def __get_current_date__(self):
        return f"{datetime.now()}"
    
    def __get_payload__(self, data:dict, type:str="admin"):
        return {
            "type": type,
            "date": self.__get_current_date__(),
            "data": data
        }

    def generate_jwt(self, data:dict):
        return jwt.encode(self.__get_payload__(data, "admin"), 
                                    self.jwt_secret, 
                                    algorithm="HS256")
    
    def get_decoded_jwt(self, token) -> list[str]:
        return [jwt.decode(token, 
                           self.jwt_secret, 
                           algorithms=["HS256"])]

if __name__ == "__main__":
    jwtHandler = JwtKey()
    data = {
            "login": "test",
            "secret_key": "1234567890123456"
        }
    jwtKey = jwtHandler.generate_jwt(data)
    print(jwtKey)
    print(jwtHandler.get_decoded_jwt(jwtKey))