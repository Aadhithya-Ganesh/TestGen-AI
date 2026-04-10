from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.agent.tools.docker.run_container import run_container
from app.agent.tools.code.update_db import update_job


MODEL_GPT_4_MINI = "openai/gpt-4.1-mini"

try:
    docker_agent = LlmAgent(
        # Using a potentially different/cheaper model for a simple task
        model=LiteLlm(model=MODEL_GPT_4_MINI),
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="docker_agent",
        instruction="""You are a Docker Agent.

            Your ONLY job is to:
            - choose the correct base image based on language
            - run a container using the run_container tool

            Rules:
            - ALWAYS call the tool
            - AFTER running the container, return ONLY the container_id
            - DO NOT ask questions
            - DO NOT end the conversation
            - DO NOT provide explanations

            Output format (STRICT):
            {
            "container_id": "<id>"
            }
            
            Once you finish running the container, use the update_job tool to update the containerCreated field to True.
            This is the Schema.

            {
                "job_id": job_id,
                "user_id": user["github_id"],
                "repo_url": repo_url,
                "language": language,
                "containerCreated": False,
                "repoCloned": False,
                "analysisComplete": False,
                "initialCoverage": None,
                "currentCoverage": None,
                "finalCoverage": None,
                "files": [],
                "created_at": datetime.now(timezone.utc),
            }
            """,
        description="Handlers Docker-related tasks with run_container and stop_container tools.",  # Crucial for delegation
        tools=[run_container, update_job],
        output_key="docker_response",  # This is the key that will be used to pass the response to the orchestrator
    )
    print(f"✅ Agent '{docker_agent.name}' created using model '{docker_agent.model}'.")
except Exception as e:
    print(
        f"❌ Could not create Docker agent. Check API Key ({docker_agent.model}). Error: {e}"  # type: ignore
    )
