from app.celery_worker import app
from app.agent.root_agent import call_agent


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def agent(
    self,
    job_id: str,
    repo: str,
    language: str,
    github_token: str,
    user_id: str,
    container_id: str,
):
    call_agent(job_id, repo, language, github_token, user_id, container_id)  # type: ignore
    return
