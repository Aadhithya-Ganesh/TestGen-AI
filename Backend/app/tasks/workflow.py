from app.celery_worker import app
from app.agent.root_agent import call_agent


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def agent(self, repo: str, language: str, github_token: str):
    call_agent(repo, language, github_token)  # type: ignore
    return
