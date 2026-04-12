import docker
import requests
import os
from datetime import datetime


def create_pull_request(
    container_id: str,
    job_id: str,
    repo_path: str = "/app",
    commit_message: str = "Add auto-generated tests",
    pr_title: str = "Automated Test Generation",
    pr_body: str = "This PR adds auto-generated tests created by TestGen AI.",
    github_token: str = None,  # type: ignore
    repo_url: str = None,  # type: ignore
):
    """
    Creates a pull request with a unique branch name derived from the job ID
    and current timestamp, using the Docker SDK for all git operations.

    Branch name format: testgen/<job_id_short>-<YYYYMMDD-HHMMSS>
    Example:           testgen/f6c8f702-20260412-145511

    Parameters
    ----------
    container_id : str
        Running container ID where the repo is cloned.
    job_id : str
        The TestGen job ID — used to make the branch name unique and traceable.
    repo_path : str
        Absolute path inside the container where the repo is cloned. Default: /app
    commit_message : str
        Git commit message.
    pr_title : str
        Title of the GitHub pull request.
    pr_body : str
        Body/description of the GitHub pull request.
    github_token : str
        GitHub personal access token with repo scope.
        Falls back to GITHUB_TOKEN env var if not provided.
    repo_url : str
        Full GitHub repo URL, e.g. https://github.com/owner/repo
        or just owner/repo.

    Returns
    -------
    dict
        {
            "status": "success",
            "pr_url": "<github pr url>",
            "branch": "<branch name>"
        }
        or
        {
            "status": "error",
            "message": "<error details>"
        }
    """
    try:
        github_token = github_token or os.getenv("GITHUB_TOKEN")  # type: ignore

        if not github_token:
            raise Exception("GitHub token not provided")

        if not repo_url:
            raise Exception("repo_url is required")

        # Extract owner/repo from URL
        repo_path_clean = repo_url.replace(".git", "").split("github.com/")[-1]
        owner, repo = repo_path_clean.strip("/").split("/")

        # Generate unique branch name
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        short_job_id = job_id.split("-")[0] if job_id else "nojob"
        branch_name = f"testgen/{short_job_id}-{timestamp}"

        # Init Docker client
        client = docker.from_env()
        container = client.containers.get(container_id)

        def exec_cmd(cmd: str, allow_fail: bool = False):
            result = container.exec_run(
                cmd=["sh", "-c", f"cd {repo_path} && {cmd}"],
                stdout=True,
                stderr=True,
            )
            output = result.output.decode().strip()
            if result.exit_code != 0 and not allow_fail:
                raise Exception(f"Command failed: {cmd}\nOutput: {output}")
            return output

        # Set git identity globally
        exec_cmd('git config --global user.email "testgen@bot.com"')
        exec_cmd('git config --global user.name "TestGen Bot"')

        # Inject token into remote URL for authenticated push
        exec_cmd(
            f"git remote set-url origin https://{github_token}@github.com/{owner}/{repo}.git"
        )

        # Create and switch to new branch
        exec_cmd(f"git checkout -b {branch_name}")

        # Stage all changes
        exec_cmd("git add .")

        # Check if there is anything to commit
        status = exec_cmd("git status --porcelain")
        if not status:
            return {
                "status": "error",
                "message": "No changes to commit — no test files were written to the container.",
            }

        # Commit
        exec_cmd(f'git commit -m "{commit_message}"')

        # Push branch
        exec_cmd(f"git push origin {branch_name}")

        # Create PR via GitHub API
        response = requests.post(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github+json",
            },
            json={
                "title": pr_title,
                "body": pr_body,
                "head": branch_name,
                "base": "main",
            },
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"GitHub API error: {response.text}")

        pr_data = response.json()

        return {
            "status": "success",
            "pr_url": pr_data.get("html_url"),
            "branch": branch_name,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }
