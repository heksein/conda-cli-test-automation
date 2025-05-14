import pytest

from utils.conda_cli_runner import CondaCliRunner


@pytest.fixture
def conda_cli_runner() -> CondaCliRunner:
    """Create a new Conda CLI runner."""
    return CondaCliRunner()