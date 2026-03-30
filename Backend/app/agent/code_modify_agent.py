from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.agent.tools.code.read_files import read_file
from app.agent.tools.code.write_files import write_files

MODEL_GPT_4_MINI = "openai/gpt-4.1-mini"


try:
    code_modify_agent = LlmAgent(
        model=LiteLlm(model=MODEL_GPT_4_MINI),
        name="code_modify_agent",
        instruction="""
            You are the Code Modify Agent.

            You generate and write test files into the repository inside the Docker container.

            Context available to you:
            - Folder structure: {git_response}
            - Container ID: {docker_response}
            - Previous analysis: {code_analysis_response}
            - Previous test results (may be empty on first run): {code_runner_response}

            Your responsibilities:
            1. Analyze the repository structure
            2. Identify source files that need test coverage
            3. Generate appropriate test files
            4. Write those test files into the container using the write_files tool

            Test generation guidelines:
            - Follow language conventions:
                - Python → pytest (test_*.py)
                - JavaScript → jest/mocha (*.test.js / *.spec.js)
                - Java → JUnit (*Test.java)
            - Place tests in appropriate locations:
                - /app/tests/
                - /app/__tests__/
                - or alongside source files if needed
            - Ensure imports and paths are correct
            - Keep tests simple but meaningful (basic coverage is fine)

            Tools available:
            1. read_file(container_id, path)
            - Use this if you need to inspect source files before writing tests

            2. write_files(files, container_id)
            - Use this to write test files into the container
            - files format:
                [
                {
                    "path": "/app/tests/test_file.py",
                    "content": "<test code>"
                }
                ]

            Execution rules:
            - ALWAYS call write_files to create or update test files
            - You may call read_file before generating tests if needed
            - DO NOT explain your reasoning
            - DO NOT return plain text

            Flow:
            1. Decide what test files are needed
            2. Generate test content
            3. Call write_files with all files
            4. Return JSON

            Output format (STRICT):
            {
            "files_created": ["<path>", "<path>"],
            "container_id": "<id>",
            "status": "tests_generated"
            }

            After completing your task:
            - You MUST transfer control back to "code_orchestrator_agent"

            DO NOT:
            - Stop early
            - Ask questions
            - Call yourself
            """,
        description="Scans the repository folder structure to detect existing test files and reports back to the orchestrator.",
        tools=[read_file, write_files],
        output_key="code_modify_response",
    )
    print(
        f"✅ Agent '{code_modify_agent.name}' created using model '{code_modify_agent.model}'."
    )
except Exception as e:
    print(
        f"❌ Could not create Code Modify agent. Check API Key ({code_modify_agent.model}). Error: {e}"  # type: ignore
    )
