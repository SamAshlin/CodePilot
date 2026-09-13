import os
import shutil
import subprocess
import uuid


BASE_DIR = "repositories"


def clone_repository(github_url: str):

    os.makedirs(BASE_DIR, exist_ok=True)

    repository_id = str(uuid.uuid4())

    repository_path = os.path.join(
        BASE_DIR,
        repository_id
    )

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            github_url,
            repository_path
        ],
        check=True
    )

    return repository_id, repository_path