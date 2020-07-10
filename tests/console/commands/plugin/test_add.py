import pytest

from poetry.__version__ import __version__
from poetry.core.packages.package import Package
from poetry.repositories.installed_repository import InstalledRepository
from poetry.utils.env import EnvManager


@pytest.fixture()
def tester(command_tester_factory):
    return command_tester_factory("plugin add")


@pytest.fixture()
def installed():
    repository = InstalledRepository()

    repository.add_package(Package("poetry", __version__))

    return repository


def test_add_no_constraint(app, repo, tester, env, installed, mocker):
    mocker.patch.object(EnvManager, "get_system_env", return_value=env)
    mocker.patch.object(InstalledRepository, "load", return_value=installed)

    repo.add_package(Package("poetry-plugin", "0.1.0"))

    tester.execute("poetry-plugin")

    expected = """\
Updating dependencies
Resolving dependencies...

Writing lock file

Package operations: 1 install, 0 updates, 0 removals

  • Installing poetry-plugin (0.1.0)
"""

    assert tester.io.fetch_output() == expected
    assert tester.command.installer.executor.installations_count == 1
    assert tester.command.poetry.file.parent == env.path
    assert tester.command.poetry.locker.file.parent == env.path

    content = tester.command.poetry.file.read()["tool"]["poetry"]
    assert "poetry-plugin" in content["dependencies"]
    assert content["dependencies"]["poetry-plugin"] == "^0.1.0"
