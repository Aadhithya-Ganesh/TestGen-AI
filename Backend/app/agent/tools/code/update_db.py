from pymongo import MongoClient
from datetime import datetime
from app.database import db


def update_job(job_id: str, updates: dict[str, any]) -> str: # type: ignore
    """
    Updates the job status in the database.

    Args:
        job_id (str): The job ID to update.
        updates (dict): Fields to update e.g. {"containerCreated": true, "currentCoverage": 87}

    Returns:
        str: Confirmation message.
    """
    db["jobs"].update_one(
        {"job_id": job_id}, {"$set": {**updates, "updated_at": datetime.now()}}
    )
    return f"Job {job_id} updated successfully."
