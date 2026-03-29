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

    # Use find to get all files and dirs
    exit_code, output = container.exec_run(
        f"find {folder_path} -not -path '*/.git/*' -not -name '.git'"
    )

    if exit_code != 0:
        return {"error": f"Failed to scan folder: {output.decode()}"}

    paths = output.decode().strip().split("\n")
    paths = [p for p in paths if p and p != folder_path]

    # Build nested dict from paths
    structure = {}
    for path in paths:
        relative = path.replace(folder_path, "").lstrip("/")
        parts = relative.split("/")
        current = structure
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    return structure
