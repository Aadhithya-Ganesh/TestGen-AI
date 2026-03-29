from fastapi import APIRouter, Depends
from app.database import db
from app.routes.auth import get_current_user
from typing import Annotated
from app.tasks.workflow import agent

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
def analyze(
    repo_url: str, language: str, user: Annotated[dict, Depends(get_current_user)]
):
    agent.delay(repo_url, language, user["github_token"])  # type: ignore
    return {"repo_url": repo_url, "language": language}
