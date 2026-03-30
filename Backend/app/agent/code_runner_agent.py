from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.agent.tools.code.read_files import read_file
from app.agent.tools.code.execute_command import exec_command

MODEL_GPT_4_MINI = "openai/gpt-4.1-mini"

try:
    code_runner_agent = LlmAgent(
        model=LiteLlm(model=MODEL_GPT_4_MINI),
        name="code_runner_agent",
        instruction="""
            You are the Code Runner Agent.

            Context:
            - Container ID: {docker_response}
            - Analysis results: {code_analysis_response}

            Your ONLY job:
            1. Read the test files listed in {code_analysis_response} using read_file
            2. Run the tests inside the container using exec_command:
               pytest /app --cov=/app --cov-report=term-missing -v
            3. Parse the output and return coverage results

            Make sure to execute the command in the correct directory and with the correct container ID. It should usually be in a folder called /app since that's where the repo is cloned.
            You have the folder_structure from the git agent. {git_response} to know where the test files are located.

            Output (STRICT JSON ONLY):
            {
                "coverage": "<percentage>",
                "passed": <number>,
                "failed": <number>,
                "output": "<raw pytest output>"
            }

            Rules:
            - ALWAYS run pytest with --cov flag
            - DO NOT modify any files
            - DO NOT install any packages
            - ONLY valid JSON, no extra text
        """,
        description="Runs tests inside the container and returns coverage results.",
        tools=[read_file, exec_command],
        output_key="code_runner_response",
    )
    print(
        f"✅ Agent '{code_runner_agent.name}' created using model '{code_runner_agent.model}'."
    )
except Exception as e:
    print(f"❌ Could not create Code Runner agent. Error: {e}")
