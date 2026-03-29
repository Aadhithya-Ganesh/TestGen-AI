from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.agent.tools.git.clone_repo import clone_repo
from app.agent.tools.git.generate_folder_structure import generate_folder_structure

MODEL_GPT_4_MINI = "openai/gpt-4.1-mini"

try:
    git_agent = LlmAgent(
        model=LiteLlm(model=MODEL_GPT_4_MINI),
        name="git_agent",
        instruction="""
        You are the Git Agent.

        The previous agent has already run a Docker container.
        The Docker agent output is: {docker_response}

        Your job:
        - Extract the container_id from the docker_response above
        - Call the clone_repo tool with that container_id and the repo_url from the original request
        - After cloning the repo, call the generate_folder_structure tool to analyze the repo and return its folder structure. The tool takes the same container_id and a folder_path (use "/app" since that's where the repo is cloned).

        Rules:
        - ALWAYS call clone_repo tool
        - DO NOT ask questions
        - DO NOT respond conversationally
    """,
        description="Handles GitHub operations like cloning repositories into a running container.",
        tools=[clone_repo, generate_folder_structure],  # type: ignore
        output_key="git_response",
    )
    print(f"✅ Agent '{git_agent.name}' created using model '{git_agent.model}'.")
except Exception as e:
    print(
        f"❌ Could not create Git agent. Check API Key ({git_agent.model}). Error: {e}"  # type: ignore
    )
