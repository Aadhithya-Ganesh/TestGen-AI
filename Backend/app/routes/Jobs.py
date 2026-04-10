from fastapi import APIRouter
from app.database import db

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
                "analysisComplete": 1,
                "currentCoverage": 1,
                "created_at": 1,
            },
        )
    )

    return {"jobs": jobs}
