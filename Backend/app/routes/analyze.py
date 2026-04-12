from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.routes.auth import get_current_user
from typing import Annotated
from app.tasks.workflow import agent
import requests
from uuid import uuid4

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
def analyze(
    repo_url: str, language: str, user: Annotated[dict, Depends(get_current_user)]
):

    repo_name = repo_url.split("/")[-1]

    user_res = requests.get(
        f"https://api.github.com/repos/{user['username']}/{repo_name}",
        headers={"Authorization": f"Bearer {user['github_token']}"},  # type: ignore
    )

    if user_res.status_code == 404:
        raise HTTPException(
            status_code=404, detail="Repository not found or access denied."
        )

    job_id = str(uuid4())

    db["jobs"].insert_one(
        {
            "job_id": job_id,
            "user_id": user["github_id"],
            "repo_url": f"{user['username']}/{repo_name}",
            "language": language,
            "containerCreated": False,
            "repoCloned": False,
            "analysisComplete": False,
            "initialCoverage": 0,
            "currentCoverage": 0,
            "finalCoverage": 0,
            "files": [],
            "created_at": datetime.now(timezone.utc),
        }
    )

    agent.delay(job_id, repo_url, language, user["github_token"], user["github_id"])  # type: ignore
    return {"message": "Analysis started", "job_id": job_id}



