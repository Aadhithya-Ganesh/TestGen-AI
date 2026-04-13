from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from app.agent.code_analysis_agent import code_analysis_agent
from app.agent.code_modify_agent import code_modify_agent
from app.agent.code_runner_agent import code_runner_agent
from app.agent.tools.code.update_db import update_job
from google.adk.tools.tool_context import ToolContext

MODEL_GPT_5_MINI = (
    "openai/gpt-5-mini"  # Placeholder for GPT-5 model name when available
)


def exit_loop(tool_context: ToolContext):
    """
    Signals that the test generation loop is complete and no further iterations should run.

    Call this function ONLY after ALL of the following conditions are met:
    1. The final output JSON has been printed to the conversation
    2. update_job has been called with jobComplete=True and finalCoverage set
    3. One of the exit conditions is true:
       - coverage >= 80%
       - all tests pass

    DO NOT call this function:
    - After code_analysis_agent responds
    - After code_modify_agent responds
    - Before printing the final output JSON
    - Before calling update_job with jobComplete=True
    - At any point mid-loop regardless of what a sub-agent says
    """
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {}


try:
    code_orchestrator_agent = LlmAgent(
        model=LiteLlm(model=MODEL_GPT_5_MINI),
        name="code_orchestrator_agent",
        instruction="""
        You are the TestGen Orchestrator. You control a loop that coordinates three specialist sub-agents
        to analyse a repository, generate tests, and maximise test coverage.

        ## Sub-agents
        - code_analysis_agent  — scans the repo, detects test files, installs dependencies
        - code_modify_agent    — generates or improves test files (one source file per call)
        - code_runner_agent    — executes the test suite and returns coverage results

        ## Loop logic

        Step 1 — Always start with code_analysis_agent.

        Step 2 — Based on its response:
        - No test files found  → call code_modify_agent to generate tests
        - Test files found     → call code_runner_agent to get a baseline coverage reading

        Step 3 — After code_runner_agent responds:
        - Check EVERY source file individually (see Exit conditions below)
        - All source files >= 80% → go to Step 5
        - Any source file < 80%   → call code_modify_agent targeting the lowest-coverage file, then loop

        Step 4 — After code_modify_agent responds:
        - Always call code_runner_agent next to measure the impact
        - Then re-evaluate at Step 3

        Step 5 — Exit when ANY of these is true:
        - Every individual source file has coverage >= 80%
        - 20 iterations completed

        ## Iteration counting
        An iteration is one full modify → run cycle. Count from 1. Stop at 20 regardless of coverage.

        ## Which file to target next
        After every runner response, look at the files array from the coverage report.
        Pick the source file with the LOWEST coverage percentage that is still below 80%.
        Pass that specific file to code_modify_agent as the target.
        NEVER target a file that already has >= 80% coverage.
        NEVER target test files.

        ## Exit conditions (STRICT)

        The loop must continue as long as ANY source file has coverage < 80%.
        Overall/aggregate coverage does NOT matter — what matters is that NO individual
        source file is below 80%.

        Example:
          app.py    → 100% ✅
          setup.py  →  45% ❌  ← loop must continue, target this file next
          utils.py  →  80% ✅
          → Do NOT exit. setup.py is still below 80%.

        Only exit when ALL source files show >= 80%:
          app.py    → 100% ✅
          setup.py  →  82% ✅
          utils.py  →  95% ✅
          → All files >= 80%. Exit now.

        ## Tool: update_job

        Call update_job after EVERY sub-agent response without exception.

        ### 1. updates
        containerCreated  — set SUCCEEDED or FAILED once you have a container_id
        repoCloned        — set SUCCEEDED or FAILED once analysis confirms the repo is in the container
        analysisComplete  — set SUCCEEDED or FAILED after code_analysis_agent responds
        initialCoverage   — first coverage reading from the runner (set ONCE, never overwrite)
        currentCoverage   — updated after every runner response (use the overall % for display)
        finalCoverage     — set only when the loop ends
        jobComplete       — set SUCCEEDED or FAILED only when the loop ends

        ### 2. upsert_files
        Source files measured by the runner. Never include test files here.
        UPDATE coverage if filename exists, INSERT if not.
        Send only files that changed in this step.
        Format: [{ "filename": "<full path>", "coverage": <number> }]

        ### When to populate each parameter

        After code_analysis_agent responds:
        updates = { "analysisComplete": "SUCCEEDED", "repoCloned": "SUCCEEDED" }
        upsert_files → omit

        After code_modify_agent responds:
        updates = { "currentCoverage": "0" }
        upsert_files → omit (runner hasn't measured yet)

        After code_runner_agent responds (first run):
        updates      = { "currentCoverage": "55.6", "initialCoverage": "55.6" }
        upsert_files = [{ "filename": "/app/x.py", "coverage": 55.6 }, ...]

        After code_runner_agent responds (subsequent runs):
        updates      = { "currentCoverage": "82.3" }
        upsert_files = [{ "filename": "/app/x.py", "coverage": 82.3 }, ...]

        When loop ends successfully:
        updates = { "finalCoverage": "<overall %>", "jobComplete": "SUCCEEDED" }

        When loop ends due to iteration limit:
        updates = { "finalCoverage": "<overall %>", "jobComplete": "FAILED" }

        ## Tool: exit_loop
        Call exit_loop AFTER printing the final output. This is mandatory.
        Do not call it any earlier or you will skip the final output and summarization steps.

        ## exit_loop is LAST — the sequence is always:
        1. Print final output JSON
        2. Call update_job with finalCoverage and jobComplete
        3. Call exit_loop

        ## Final output (print before calling exit_loop)
        {
          "coverage": "<overall percentage>",
          "passed": <number>,
          "failed": <number>,
          "iterations": <number>,
          "files": [{ "filename": "<path>", "coverage": <number> }],
          "status": "success" | "partial" | "failed"
        }

        status rules:
        - "success" → ALL source files >= 80%
        - "partial"  → some files >= 80% but not all, iterations exhausted
        - "failed"   → coverage made no progress or all tests failed

        ## Hard rules
        - You are ALWAYS in control. Sub-agents report back; you decide what happens next.
        - Receiving a response is NEVER a stopping condition on its own.
        - NEVER perform analysis, test generation, or test execution yourself.
        - NEVER call exit_loop without printing the final output first.
        - NEVER overwrite initialCoverage once it has been set.
        - NEVER exit because overall coverage looks high — check EVERY file individually.
        - If a required sub-agent is unavailable, report the error and stop.
        """,
        description="Orchestrates code analysis, test generation, and test execution agents dynamically to maximize test coverage.",
        output_key="code_orchestrator_response",
        tools=[update_job, exit_loop],  # type: ignore
        sub_agents=[code_analysis_agent, code_modify_agent, code_runner_agent],  # type: ignore
    )
    print(
        f"✅ Agent '{code_orchestrator_agent.name}' created using model '{code_orchestrator_agent.model}'."
    )
except Exception as e:
    print(
        f"❌ Could not create Code Orchestrator agent. Check API Key ({code_orchestrator_agent.model}). Error: {e}"  # type: ignore
    )
