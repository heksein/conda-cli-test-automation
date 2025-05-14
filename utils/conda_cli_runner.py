import subprocess
import logging
import shlex
import sys
from typing import Self


logger = logging.getLogger(__name__)

class CondaCliRunner:

    def __init__(self):
        self._command: list[str] = []

    def run(self) -> subprocess.CompletedProcess:
        """
        Execute the constructed Conda CLI command.

        Returns:
            subprocess.CompletedProcess: The result of the executed command, including stdout and stderr.
        """
        logger.info(f"Running command: {shlex.join(self._command)}")
        result = subprocess.run(self._command, capture_output=True, text=True, shell=sys.platform.startswith("win"))
        logger.debug(f"Command output: {result.stdout}")
        if result.stderr:
            logger.error(f"Error running command: {result.stderr}")
        return result
    
    def with_json_output(self) -> Self:
        """
        Add the `--json` option to the command.
        """
        self._command.append("--json")
        return self
    
    def list_conda_envs(self) -> Self:
        """
        List all Conda environments.
        """
        self._command = ["conda", "env", "list"]
        return self

    def create_conda_env(self, env_name: str, python_version: str | None = None) -> Self:
        """
        Create a new Conda environment.

        Args:
            env_name (str): The name of the new Conda environment.
            python_version (str | None): The Python version to use. Defaults to None.
        """
        self._command = ["conda", "create", "-y", "-n", env_name]
        if python_version:
            self._command.append(f"python={python_version}")
        return self

    def search_conda_package(self, pkg_name: str) -> Self:
        """
        Search for a package in the Conda repository.

        Args:
            pkg_name (str): The name of the package to search for.
        """
        self._command = ["conda", "search", pkg_name]
        return self

    def install_conda_packages(self, env_name: str, packages: dict) -> Self:
        """
        Install packages in the specified Conda environment. If the version is "latest", just package name 
        is added to the command. Otherwise, the package name and version are added to the command.
        Args:
            env_name (str): The name of the Conda environment.
            packages (dict): The list of packages with their versions to install.
        """
        self._command = ["conda", "install", "-y", "-n", env_name]
        for pkg, version in packages.items():
            self._command.append(f"{pkg}={version}" if version else pkg)
        return self

    def list_conda_packages(self, env_name: str) -> Self:
        """
        List all packages in the specified Conda environment.

        Args:
            env_name (str): The name of the Conda environment.
        """
        self._command = ["conda", "list", "-n", env_name]
        return self

    def remove_conda_env(self, env_name: str) -> Self:
        """
        Remove the specified Conda environment.

        Args:
            env_name (str): The name of the Conda environment.
        """
        self._command = ["conda", "env", "remove", "-y", "-n", env_name]
        return self