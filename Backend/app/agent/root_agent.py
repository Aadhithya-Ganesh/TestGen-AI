from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import asyncio
from google.genai import types
from app.agent.docker_agent import docker_agent
from app.agent.git_agent import git_agent

MODEL_GPT_4_MINI = "openai/gpt-4.1-mini"

APP_NAME = "testgen_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


def create_agent():
    test_gen_agent = SequentialAgent(
        name="test_gen_pipeline_agent",
        sub_agents=[docker_agent, git_agent],  # type: ignore
        description="Executes a sequence of tasks using Docker and Git agents to create repositories and run containers based on user queries.",
    )

    print(f"Agent '{test_gen_agent.name}' created using model '{MODEL_GPT_4_MINI}'.")

    return test_gen_agent


async def init_session(
    app_name: str, user_id: str, session_id: str
) -> InMemorySessionService:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    print(
        f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'"
    )

    return session_service


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        # You can uncomment the line below to see *all* events during execution
        print(
            f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}"
        )

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif (
                event.actions and event.actions.escalate
            ):  # Handle potential errors/escalations
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            # Add more checks here if needed (e.g., specific error codes)

    print(f"<<< Agent Response: {final_response_text}")


def call_agent(repo, language, github_token):
    agent = create_agent()
    session = asyncio.run(init_session(APP_NAME, USER_ID, SESSION_ID))

    runner = Runner(
        agent=agent,  # The agent we want to run
        app_name=APP_NAME,  # Associates runs with our app
        session_service=session,  # Uses our session manager
    )

    print(f"Runner created for agent '{runner.agent.name}'.")

    async def run_conversation():
        await call_agent_async(
            query=f"Analyze the repository: {repo} with language: {language}. GitHub token: {github_token}",
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")
