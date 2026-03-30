import docker
import io
import tarfile
import os


def write_files(files: list[dict[str, str]], container_id: str) -> dict:
    """
    Write multiple files into a Docker container.

    Args:
        files: List of dicts, each with 'path' (str) and 'content' (str) keys.
               Example: [{"path": "/app/requirements.txt", "content": "pytest\n"}]
        container_id: Docker container ID.

    Returns:
        dict: Status and number of files written.
    """

    client = docker.from_env()
    container = client.containers.get(container_id)

    for file in files:
        path = file["path"]
        content = file["content"]

        dir_path = os.path.dirname(path)
        file_name = os.path.basename(path)

        # 1. Ensure directory exists
        container.exec_run(f"mkdir -p {dir_path}")

        # 2. Create tar archive in memory
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            file_data = content.encode("utf-8")

            tarinfo = tarfile.TarInfo(name=file_name)
            tarinfo.size = len(file_data)

            tar.addfile(tarinfo, io.BytesIO(file_data))

        tar_stream.seek(0)

        # 3. Copy into container
        container.put_archive(path=dir_path, data=tar_stream)

    return {"status": "success", "files_written": len(files)}
