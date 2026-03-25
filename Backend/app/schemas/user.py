from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str


class UserResponse(BaseModel):
    github_id: int
    username: str
    avatar_url: str | None = None
    html_url: str | None = None
