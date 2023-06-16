import time, jwt
from exceptions.errors import AuthenticationError


class AuthHandler:
    def __init__(self, JWT_SECRET_KEY: str, JWT_ALGORITHM: str) -> None:
        self.__JWT_ALGORITHM = JWT_ALGORITHM
        self.__JWT_SECRET = JWT_SECRET_KEY

    def decodeJwt(self, token):
        try:
            decoded_token = jwt.decode(
                token, key=self.__JWT_SECRET, algorithms=[self.__JWT_ALGORITHM]
            )
            decoded_token = (
                decoded_token if decoded_token["exp"] >= time.time() else None
            )
            return decoded_token
        except Exception:
            raise AuthenticationError(message="Invalid token or expired token")

    def signJwt(self, payload: dict):
        payload.update({"exp": time.time() + 100592000})
        token = jwt.encode(
            payload, key=self.__JWT_SECRET, algorithm=self.__JWT_ALGORITHM
        )
        return token
