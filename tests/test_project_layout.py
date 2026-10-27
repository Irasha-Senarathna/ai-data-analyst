"""Smoke tests for the repo scaffold: folders, packages and config template."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

PYTHON_PACKAGES = ["agent", "api", "evals", "pipeline", "semantic"]
REQUIRED_ENV_KEYS = [
    "LLM_PROVIDER",
    "LLM_MODEL_SQL",
    "LLM_MODEL_ANSWER",
    "OLLAMA_BASE_URL",
    "KAGGLE_USERNAME",
    "KAGGLE_KEY",
    "JWT_SECRET",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_HOST",
]


def read_env_keys(path: Path) -> set[str]:
    keys = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0])
    return keys


@pytest.mark.parametrize("package", PYTHON_PACKAGES)
def test_python_package_exists(package: str) -> None:
    assert (ROOT / package / "__init__.py").is_file()


@pytest.mark.parametrize("folder", ["dbt", "docs", "web"])
def test_folder_exists(folder: str) -> None:
    assert (ROOT / folder).is_dir()


def test_env_example_has_required_keys() -> None:
    keys = read_env_keys(ROOT / ".env.example")

    missing = [key for key in REQUIRED_ENV_KEYS if key not in keys]

    assert missing == []


def test_env_example_defaults_to_ollama() -> None:
    text = (ROOT / ".env.example").read_text()

    assert "LLM_PROVIDER=ollama" in text
