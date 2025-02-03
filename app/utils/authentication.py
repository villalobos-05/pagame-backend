from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
import jwt
import uuid

load_dotenv()


class JwtPayload:
    sub: str  # id
    exp: datetime


def createAccessToken(data: JwtPayload, expireTime: timedelta | None = None):
    toEncode = data.copy()

    expire = datetime.now(timezone.utc) + (expireTime or timedelta(minutes=15))

    toEncode.update({"exp": expire})

    return jwt.encode(
        toEncode, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )


def createRefreshToken():
    refreshToken = str(uuid.uuid4())
    return refreshToken
