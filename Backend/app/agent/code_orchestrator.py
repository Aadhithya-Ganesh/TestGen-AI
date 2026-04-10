from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.agent.code_analysis_agent import code_analysis_agent
from app.agent.code_modify_agent import code_modify_agent
from app.agent.code_runner_agent import code_runner_agent
from app.agent.tools.code.update_db import update_job

MODEL_GPT_4_MINI = (
    "openai/gpt-4.1-mini"  # Placeholder for GPT-5 model name when available
)

try:
    code_orchestrator_agent = LlmAgent(
        model=LiteLlm(model=MODEL_GPT_4_MINI),
        name="code_orchestrator_agent",
        instruction="""
            You are the Code Orchestrator Agent for TestGen AI.

            You coordinate 3 specialist sub-agents in a loop.

            Sub-agents:
            1. 'code_analysis_agent': Scans repo for existing test files. Returns has_tests, test_files, container_id.
            2. 'code_modify_agent': Generates or fixes tests. Pass it source files and failure details.
            3. 'code_runner_agent': Runs tests and returns coverage, passed, failed.

            Flow:
            - Call code_analysis_agent first
            - When it returns, YOU decide what to do next based on its output
            - If has_tests is false → call code_modify_agent to generate tests
            - If has_tests is true → call code_runner_agent to get current coverage
            - After running tests → if coverage < 80% call code_modify_agent to improve
            - Repeat up to 3 times

            Rules:
            - YOU are always in control
            - Sub-agents report back to YOU automatically — you do not need to pull results
            - NEVER do analysis, generation or execution yourself
            - Stop when coverage > 80%, all tests pass, or 3 iterations exhausted
            - If agents are missing, say you cannot process and stop

            You MUST keep calling sub-agents until one of these is true:
            - coverage > 80%
            - all tests pass  
            - 3 iterations exhausted

            You are NOT done after code_analysis_agent responds.
            Receiving a response from a sub-agent is NOT a stopping condition.
            ALWAYS decide what to call next after every sub-agent response.

            CRITICAL:

            You are in a continuous control loop.

            After ANY sub-agent response:
            - You MUST continue execution
            - You MUST decide the next agent to call

            The system will NOT automatically continue for you.
            You must explicitly call the next agent.

            DO NOT stop after code_analysis_agent.

            If:
            - has_tests = false → call code_modify_agent
            - has tests and you dont know coverage = true → call code_runner_agent
            - has_tests and coverage < 80% = true → call code_modify_agent
            - If you just wrote tests or improved them → call code_runner_agent to check results
            - iterations >= 5 → Just report back the current results and stop

            When you call the subagents to do their tasks and when they reply you back the with results, you must call the update_job tool to update the database with the latest information. 
            This is CRITICAL to ensure the system has the most up-to-date information on the job status.
            When you get info about the files that are changes, add that to the files field with file name as key and the content that you wrote as the value. This will help us keep track of what changes were made to the codebase during the process.
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
                "files": object,
                "created_at": datetime.now(timezone.utc),
            }

            For example,
            1. If there are test cases, Run them and get coverage and set initialCoverage and currentCoverage to the same value. Then if coverage is less than 80%, call code_modify_agent to improve tests. After that call code_runner_agent again to check coverage and set currentCoverage to the new value. Repeat this until you have >80% coverage or you exhaust 5 iterations.
            2. If there are no test cases, call code_modify_agent to generate tests. After that call code_runner_agent to run them and get coverage. Set initialCoverage to 0 and
            currentCoverage to the new value. If coverage is less than 80%, call code_modify_agent again to improve tests. After that call code_runner_agent again to check coverage and set currentCoverage to the new value. Repeat this until you have >80% coverage or you exhaust 5 iterations.
            3. If at any point you exhaust 5 iterations, just report back the current coverage and test results without calling any more agents.
            4. When you are done with everything, Update the analysisComplete field to True and finalCoverage to the latest coverage value.

            Final output format (STRICT):
            {
                "coverage": "<percentage>",
                "passed": <number>,
                "failed": <number>,
                "iterations": <number>,
                "status": "success" | "partial" | "failed"
            }
        """,
        description="Orchestrates code analysis, test generation, and test execution agents dynamically to maximize test coverage.",
        output_key="code_orchestrator_response",
        tools=[update_job],  # type: ignore
        sub_agents=[code_analysis_agent, code_modify_agent, code_runner_agent],  # type: ignore
    )
    print(
        f"✅ Agent '{code_orchestrator_agent.name}' created using model '{code_orchestrator_agent.model}'."
    )
except Exception as e:
    print(
        f"❌ Could not create Code Orchestrator agent. Check API Key ({code_orchestrator_agent.model}). Error: {e}"  # type: ignore
    )
