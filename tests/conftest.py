import pytest
from click.testing import CliRunner


@pytest.fixture
def app():
    memo_app = CliRunner()
    yield memo_app
