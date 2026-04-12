# app/agent/tools/code/save_diff.py

import docker
from app.database import db


def save_diff(job_id: str, container_id: str, file_path: str) -> dict:
    """
    Runs git diff on a single file inside the container after it has been
    written, and saves the diff to the job's tests array in the database.

    Uses the Docker SDK (docker socket) — works correctly from inside a container.

    - If the file is tracked by git: uses git diff
    - If the file is untracked (new file): uses git diff --no-index /dev/null <file>
    - Upserts into the tests array:
        - If an entry with this filename already exists: updates only the diff field
        - If no entry exists: inserts a new entry with filename, diff, and coverage: 0

    Parameters
    ----------
    job_id : str
        The job ID to update in the database.
    container_id : str
        The running container ID to execute the git diff command in.
    file_path : str
        Absolute path of the single file inside the container that was just written.
        Example: /app/test_auth.py

    Returns
    -------
    dict
        {
            "filename": "<file_path>",
            "diff": "<raw git diff output>",
            "status": "saved" | "no_changes" | "error"
        }

    Examples
    --------
    save_diff("job-123", "bf8d88583af8", "/app/test_auth.py")
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)

        # Try diff for tracked files first
        _, output = container.exec_run(["git", "-C", "/app", "diff", "--", file_path])
        diff = output.decode("utf-8").strip()

        # If empty, file is untracked — diff against /dev/null
        if not diff:
            _, output = container.exec_run(
                ["git", "-C", "/app", "diff", "--no-index", "/dev/null", file_path]
            )
            diff = output.decode("utf-8").strip()

        if not diff:
            return {"filename": file_path, "diff": "", "status": "no_changes"}

        # Upsert — update diff field only if entry exists, never wipe content/coverage
        result = db.jobs.update_one(
            {"job_id": job_id, "tests.filename": file_path},
            {"$set": {"tests.$.diff": diff}},
        )

        if result.matched_count == 0:
            # New file — insert fresh entry
            db.jobs.update_one(
                {"job_id": job_id},
                {
                    "$push": {
                        "tests": {
                            "filename": file_path,
                            "diff": diff,
                            "coverage": 0,
                        }
                    }
                },
            )

        return {"filename": file_path, "diff": diff, "status": "saved"}

    except Exception as e:
        return {"filename": file_path, "diff": "", "status": "error", "error": str(e)}
