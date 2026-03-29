import docker

client = docker.from_env()


def clone_repo(container_id: str, repo_url: str) -> str:
    """
    Simulates cloning a Git repository into a Docker container.

    Args:
        repo_url (str): The URL of the Git repository to clone.
        container_id (str): The ID of the Docker container where the repo should be cloned.

    Returns:
        str: A message indicating the result of the cloning operation.
    """

    container = client.containers.get(container_id)

    # Install git
    container.exec_run("apt-get update && apt-get install -y git")

    # Clone using env variable (IMPORTANT: use sh -c)
    clone_cmd = (
        "sh -c 'git clone https://$GITHUB_TOKEN@"
        + repo_url.replace("https://", "")
        + " /app'"
    )

    exit_code, output = container.exec_run(clone_cmd)

    if exit_code != 0:
        return f"Error cloning repo: {output.decode()}"

    return (
        f"Repository '{repo_url}' successfully cloned into container '{container_id}'."
    )
