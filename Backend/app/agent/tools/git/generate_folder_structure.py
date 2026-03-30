import os

import docker
import json

client = docker.from_env()


def generate_folder_structure(container_id: str, folder_path: str) -> dict:
    """
    Scans a folder inside a running Docker container and returns its structure.

    Args:
        container_id (str): The ID of the running Docker container.
        folder_path (str): The path inside the container to scan.

    Returns:
        dict: Nested dictionary representing the folder structure.
    """
    container = client.containers.get(container_id)

    exit_code, output = container.exec_run(
        f"find {folder_path} -type f -not -path '*/.git/*'"
    )

    if exit_code != 0:
        return {"error": output.decode()}

    paths = output.decode().strip().split("\n")

    files = []
    for path in paths:
        path = path.strip()

        if not path:
            continue

        # ✅ robust relative path
        relative = os.path.relpath(path, folder_path)

        # skip weird results
        if relative.startswith(".."):
            continue

        files.append(relative)

    return {"files": files}
