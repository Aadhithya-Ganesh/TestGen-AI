from app.celery_worker import app
from app.agent.my_agent.agent import call_agent


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def add(self, x: int, y: int) -> int:
    call_agent()
    return x + y
