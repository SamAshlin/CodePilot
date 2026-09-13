import os
import subprocess
import uuid
import shutil
import requests


BASE_DIR = "repositories"


def normalize_github_url(github_url: str):

    github_url = github_url.strip()

    if github_url.endswith("/"):
        github_url = github_url[:-1]

    if github_url.endswith(".git"):
        github_url = github_url[:-4]

    return github_url


def get_repository_key(github_url: str):

    github_url = normalize_github_url(
        github_url
    )

    parts = github_url.split("/")

    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub repository URL"
        )

    owner = parts[-2]
    repo = parts[-1]

    return f"{owner}/{repo}"


def get_remote_commit_sha(github_url: str):

    github_url = normalize_github_url(
        github_url
    )

    parts = github_url.split("/")

    owner = parts[-2]
    repo = parts[-1]

    api_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits"
    )

    response = requests.get(
        api_url,
        headers={
            "Accept": "application/vnd.github+json"
        },
        params={
            "per_page": 1
        },
        timeout=10
    )

    response.raise_for_status()

    commits = response.json()

    if not commits:
        raise RuntimeError(
            "Could not determine latest commit SHA"
        )

    return commits[0]["sha"]


def get_current_commit_sha(repository_path):

    result = subprocess.run(
        [
            "git",
            "-C",
            repository_path,
            "rev-parse",
            "HEAD"
        ],
        check=True,
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


def clone_repository(
    github_url,
    repository_id=None
):

    os.makedirs(
        BASE_DIR,
        exist_ok=True
    )

    # ------------------------------------------
    # Stable repository ID
    # ------------------------------------------

    if repository_id is None:

        repository_id = str(
            uuid.uuid4()
        )

    # ------------------------------------------
    # Create a TEMPORARY clone directory
    #
    # The directory name is different every time.
    # ------------------------------------------

    clone_id = str(
        uuid.uuid4()
    )

    repository_path = os.path.join(
        BASE_DIR,
        f"clone_{clone_id}"
    )

    # ------------------------------------------
    # Clone repository
    # ------------------------------------------

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

    # ------------------------------------------
    # Get actual commit from cloned repository
    # ------------------------------------------

    commit_sha = get_current_commit_sha(
        repository_path
    )

    return (
        repository_id,
        repository_path,
        commit_sha
    )