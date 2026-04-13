from app.database import db


TEST_FILE_PATTERNS = (
    "test_",
    "_test.",
    ".test.",
    "_spec.",
    "/test/",
    "/tests/",
    "/__tests__/",
)


def update_job(
    job_id: str,
    updates: dict = None,  # type: ignore
    upsert_files: list = None,  # type: ignore
):
    """
    Update a job record in the database.

    Used by the docker_agent, git_agent, and code_orchestrator_agent to keep
    the job record current throughout the pipeline.

    Parameters
    ----------
    job_id : str
        The unique identifier of the job to update.

    updates : dict, optional
        Fields to set directly on the job document. Supports any top-level
        job field, for example:
            {
                "containerCreated": "IN-PROGRESS" | "FAILED" | "SUCCEEDED",
                "container_id": "1d510f697245",
                "repoCloned": "IN-PROGRESS" | "FAILED" | "SUCCEEDED",
                "analysisComplete": "IN-PROGRESS" | "FAILED" | "SUCCEEDED",
                "initialCoverage": "20.9",   # set ONCE, never overwrite
                "currentCoverage": "74.5",
                "finalCoverage": "100.0",    # set only when loop ends
                "jobComplete": "IN-PROGRESS" | "FAILED" | "SUCCEEDED" # set only when loop ends
            }

    upsert_files : list, optional
        Source file coverage entries measured by the runner agent.
        Each entry is UPSERTed — updated if the filename already exists
        in the files array, inserted if it does not.
        Test files are silently stripped before writing regardless of what
        is passed in.
        Only updates coverage — never overwrites filename or content.
        Send only the files that changed in this step, never the full array.
        Format:
            [{ "filename": "/app/auth.py", "coverage": 74.5 }]

    Notes
    -----
    Test file tracking (content, diff) is handled exclusively by save_diff.
    Do not pass test files to upsert_files — they are silently stripped.

    Returns
    -------
    None

    Examples
    --------
    # docker_agent — container created
    update_job("job-123", updates={"containerCreated": True, "container_id": "1d510f697245"})

    # orchestrator — after runner agent measures coverage
    update_job(
        "job-123",
        updates={"currentCoverage": "74.5"},
        upsert_files=[{"filename": "/app/auth.py", "coverage": 74.5}],
    )

    # orchestrator — loop complete
    update_job("job-123", updates={"finalCoverage": "100.0", "jobComplete": True})
    """

    if upsert_files:
        # Strip test files unconditionally
        upsert_files = [
            f
            for f in upsert_files
            if not any(
                p in f["filename"] for p in ("test_", "_test.", ".test.", "_spec.")
            )
        ]
        for entry in upsert_files:
            # Only update coverage — never overwrite the whole entry
            result = db.jobs.update_one(
                {"job_id": job_id, "files.filename": entry["filename"]},
                {"$set": {"files.$.coverage": entry["coverage"]}},
            )
            if result.matched_count == 0:
                db.jobs.update_one(
                    {"job_id": job_id},
                    {
                        "$push": {
                            "files": {
                                "filename": entry["filename"],
                                "coverage": entry["coverage"],
                            }
                        }
                    },
                )

    if updates:
        db.jobs.update_one({"job_id": job_id}, {"$set": updates})
