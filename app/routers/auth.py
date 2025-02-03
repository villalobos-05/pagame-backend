import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.models.user import CreateUser, LogUser
from app.utils.authentication import createAccessToken, createRefreshToken

router = APIRouter(prefix="/auth", tags=["authentication"])

# Password hashing context
pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticateUser(
    db: AsyncIOMotorDatabase,
    password: str,
    username: str | None = None,
    email: str | None = None,
):
    if email:
        query = {"email": email}
    elif username:
        query = {"username": username}
    else:
        return False

    user = await db["users"].find_one(query)

    if not user or not pwdContext.verify(password, user["password"]):
        return False

    return user


# Endpoints
@router.post("/sign-in")
async def signIn(
    user: LogUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    loggedUser = await authenticateUser(db, user.password, user.username, user.email)

    if not loggedUser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    accessToken = createAccessToken(
        data={"sub": str(loggedUser["_id"])},
        expireTime=timedelta(minutes=15),
    )

    refreshToken = createRefreshToken()

    await db["users"].update_one(
        {"_id": loggedUser["_id"]}, {"$set": {"refreshToken": refreshToken}}
    )

    return {
        "access_token": accessToken,
        "refresh_token": refreshToken,
    }


@router.post("/sign-up")
async def signUp(
    user: CreateUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    existingUser = await db["users"].find_one({"email": user.email})

    if existingUser:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    usernamePicked = await db["users"].find_one({"username": user.username})

    if usernamePicked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already picked",
        )

    # todo: check email

    userDict = user.model_dump()
    userDict["password"] = pwdContext.hash(user.password)

    userDict["refreshToken"] = createRefreshToken()

    userDict["createdAt"] = datetime.now(timezone.utc)

    data = await db["users"].insert_one(userDict)

    return {
        "message": "User created successfully",
        "access_token": createAccessToken(data={"sub": str(data.inserted_id)}),
        "refresh_token": userDict["refreshToken"],
    }


@router.post("/refresh-token")
async def refreshToken(
    refreshToken: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    # todo check authenticated user
    user = await db["users"].find_one({"refreshToken": refreshToken})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    newAccessToken = createAccessToken(
        data={"sub": user["_id"]},
        expireTime=timedelta(minutes=15),
    )

    newRefreshToken = createRefreshToken()
    await db["users"].update_one(
        {"_id": user["_id"]}, {"$set": {"refreshToken": newRefreshToken}}
    )

    return {
        "access_token": newAccessToken,
        "refresh_token": newRefreshToken,
    }
