import os


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".md": "markdown",
    ".txt": "text",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml"
}


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "coverage"
}


def scan_repository(repository_path):

    files = []

    for root, directories, filenames in os.walk(repository_path):

        directories[:] = [
            d for d in directories
            if d not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:

            extension = os.path.splitext(filename)[1].lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            full_path = os.path.join(
                root,
                filename
            )

            try:

                with open(
                    full_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    content = file.read()

                relative_path = os.path.relpath(
                    full_path,
                    repository_path
                )

                files.append({
                    "path": relative_path,
                    "language": SUPPORTED_EXTENSIONS[extension],
                    "content": content
                })

            except Exception:
                continue

    return files