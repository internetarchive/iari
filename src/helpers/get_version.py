# get_version.py

from datetime import datetime


def get_poetry_version(file_path):
    with open(file_path) as toml_file:
        content = toml_file.read()

        poetry_start = content.find("[tool.poetry]")
        if poetry_start == -1:
            return None  # The [tool.poetry] section is not found

        version_start = content.find("version", poetry_start)
        if version_start == -1:
            return None  # The 'version' property is not found in [tool.poetry]

        version_end = content.find("\n", version_start)
        version_line = content[version_start:version_end].strip()

        # Assuming version is in the format 'version = "x.y.z"'
        version = version_line.split("=")[1].strip().strip('"')

        return version


def get_version_stamp():
    now = datetime.utcnow()
    return {
        "iari_version": get_poetry_version("pyproject.toml"),
        "timestamp": int(datetime.timestamp(now)),
        "isodate": str(datetime.isoformat(now)),
    }
