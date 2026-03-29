import docker

client = docker.from_env()


def run_container(image_name, git_token) -> str:
    """
    Runs a Docker container with the specified image name.
    Args:
        image_name (str): The name of the Docker image to run (e.g., 'nginx', 'python:3.8').
        token (str): The GitHub authentication token.
    Returns:
        str: A message indicating the result of the operation.
    """
    container = client.containers.run(
        image_name,
        command="tail -f /dev/null",  # keeps container alive
        environment={
            "GITHUB_TOKEN": git_token  # inject here
        },
        detach=True,
    )

    return f"Container '{container.short_id}' is running with image '{image_name}'."
