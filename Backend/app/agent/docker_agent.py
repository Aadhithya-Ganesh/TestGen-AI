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
        instruction="""
            You are the Docker Agent.

            Your ONLY job is to spin up a container for the repository to run inside.

            ## Task
            1. Choose the correct base image based on the language provided:
            - python → python:latest
            - node   → node:latest
            - java   → maven:latest
            - go     → golang:latest
            - ruby   → ruby:latest

            2. Call run_container with the chosen image and the git_token.

            3. Call update_job with:
            updates = { "containerCreated": "FAILED" | "SUCCEEDED", "container_id": "<id>" }

            ## Output (STRICT JSON, no other text)
            {
            "container_id": "<id>"
            }

            ## Rules
            - ALWAYS call run_container first, then update_job.
            - NEVER ask questions or provide explanations.
            - NEVER proceed without calling both tools.
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
