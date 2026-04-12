from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException
from app.routes.auth import get_current_user
from app.database import db
from app.tasks.workflow import agent

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs")
def get_jobs():
    jobs = list(
        db["jobs"].find(
            {},
            {
                "_id": 0,
                "job_id": 1,
                "repo_url": 1,
                "jobComplete": 1,
                "currentCoverage": 1,
                "created_at": 1,
            },
        )
    )

    return {"jobs": jobs}


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = db["jobs"].find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        return {"error": "Job not found"}
    return job


@router.post("/jobs/create_pull_request/{job_id}")
def create_pull_request(job_id: str, user: Annotated[dict, Depends(get_current_user)]):
    job = db["jobs"].find_one({"job_id": job_id, "user_id": user["github_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if not job.get("analysisComplete"):
        raise HTTPException(status_code=400, detail="Analysis not complete yet.")

    agent.delay(  # type: ignore
        job_id,
        job["repo_url"],
        job["language"],
        user["github_token"],
        user["github_id"],
        job["container_id"],
    )
    return {"message": "Pull request created successfully."}
