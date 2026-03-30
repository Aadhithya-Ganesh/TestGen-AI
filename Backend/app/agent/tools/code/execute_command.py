import docker


def exec_command(container_id: str, command: str) -> str:
    """
    Executes a shell command inside a running Docker container.

    Args:
        container_id (str): The container ID.
        command (str): The shell command to run.

    Returns:
        str: stdout/stderr output from the command.
    """
    client = docker.from_env()
    container = client.containers.get(container_id)

    exit_code, output = container.exec_run(f"sh -c '{command}'")

    return output.decode() if output else "No output"
