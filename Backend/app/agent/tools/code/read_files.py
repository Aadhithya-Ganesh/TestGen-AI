import docker

client = docker.from_env()


def read_file(container_id: str, file_path: str) -> str:
    """
    Reads the contents of a file inside a running Docker container.

    Args:
        container_id (str): The ID of the running Docker container.
        file_path (str): The absolute path of the file inside the container.

    Returns:
        str: The contents of the file, or an error message if it fails.
    """
    container = client.containers.get(container_id)

    exit_code, output = container.exec_run(f"cat {file_path}")

    if exit_code != 0:
        return f"Error reading file '{file_path}': {output.decode()}"

    return output.decode()
