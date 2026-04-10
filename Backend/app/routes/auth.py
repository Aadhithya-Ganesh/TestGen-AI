from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import os
import jwt
import requests
from fastapi.security import OAuth2PasswordBearer
from app.database import db
from app.schemas.user import Token, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        github_id = payload.get("sub")

        if github_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db["users"].find_one({"github_id": int(github_id)})

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/login", response_model=Token)
async def login(code: str):
    response = requests.post(
        url="https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        },
    )

    data = response.json()
    github_token = data.get("access_token")

    if not github_token:
        raise HTTPException(status_code=400, detail="GitHub auth failed")

    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {github_token}"},
    )

    github_user = user_res.json()

    github_id = github_user["id"]
    username = github_user["login"]
    avatar_url = github_user["avatar_url"]
    html_url = github_user["html_url"]

    existing_user = db["users"].find_one({"github_id": github_id})

    if not existing_user:
        db["users"].insert_one(
            {
                "github_id": github_id,
                "username": username,
                "avatar_url": avatar_url,
                "html_url": html_url,
                "github_token": github_token,
                "created_at": datetime.now(timezone.utc),
            }
        )
    else:
        db["users"].update_one(
            {"github_id": github_id},
            {
                "$set": {
                    "github_token": github_token,
                    "avatar_url": avatar_url,
                    "html_url": html_url,
                }
            },
        )

    access_token = create_access_token({"sub": str(github_id)})

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[dict, Depends(get_current_user)]):
    return {
        "github_id": user["github_id"],
        "username": user["username"],
        "avatar_url": user.get("avatar_url"),
        "html_url": user.get("html_url"),
    }
