from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from bson import ObjectId

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def getAuthenticatedUserId(token: Annotated[str, Depends(oauth2_scheme)]) -> ObjectId:
    """
    Extracts and returns the authenticated user's ID from the provided JWT token as mongo ObjectId.
    """
    try:
        payload: dict = jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        return getObjectId(payload["sub"])

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid jwt",
            headers={"WWW-Authenticate": "Bearer"},
        )


def getObjectId(id: str) -> ObjectId:
    """
    Convert and return a string id to an mongo ObjectId.
    If id is not a valid ObjectId, an HTTP 400 error is raised.

    This is done because ids in Mongodb are handled with ObjectIDs,
    and, if a wrong id (id that cannot be converted to ObjectId) is given,
    it would throw and internal 500 error.
    """
    try:
        return ObjectId(id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Id {id} is not a valid ObjectId: {str(e)}",
        )
