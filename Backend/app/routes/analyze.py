from fastapi import APIRouter, Depends
from app.database import db
from app.routes.auth import get_current_user
from typing import Annotated
from app.tasks.workflow import add

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
def analyze(
    repo_url: str, language: str, user: Annotated[dict, Depends(get_current_user)]
):
    add.delay(2, 3)  # type: ignore
    return {"repo_url": repo_url, "language": language}
