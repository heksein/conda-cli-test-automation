import logging
import json
import os
from typing import Generator

import pytest

from test_data.package_install_workflow import ENVIRONMENTS
from utils.conda_cli_runner import CondaCliRunner


logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("setup_teardown")
class TestCondaEnvWorkflow:

    def _clean_up_environments(self, conda_cli_runner: CondaCliRunner, envs_to_delete: list[str]) -> None:
        """
        Remove the specified Conda environments.

        Args:
            conda_cli_runner (CondaCliRunner): The Conda CLI runner.
            envs_to_delete (list[str]): The list of environments to delete.
        """
        for env_name in envs_to_delete:
            logger.info(f"Removing environment: {env_name}")
            result = conda_cli_runner.remove_conda_env(env_name).run()
            assert result.returncode == 0, f"Failed to remove environment: {env_name}"

    def _get_existing_test_envs(self, all_envs_json: dict) -> list[str]:
        """
        Get the list of existing Conda environments from the JSON output.

        Args:
            all_envs_json (dict): The JSON output from the `conda env list` command.
        """
        return [
            os.path.basename(env_path)
            for env_path in all_envs_json.get("envs", [])
            if "envs/" in env_path
        ]
    
    @pytest.fixture(scope="class")
    def setup_teardown(self) -> Generator[None, None, None]:
        """
        Setup and teardown fixture for the test suite to clean up the Conda environments 
        before and after the tests are run.
        """
        conda_cli_runner = CondaCliRunner()
        all_envs = conda_cli_runner.list_conda_envs().with_json_output().run()
        assert all_envs.returncode == 0, f"Failed to list environments"
        
        json_output = json.loads(all_envs.stdout)
        installed_envs = self._get_existing_test_envs(json_output)
        logger.debug(f"Installed custom environments: {installed_envs}")
        envs_to_delete = [env for env in ENVIRONMENTS.keys() if env in installed_envs]
        logger.debug(f"Environments to delete: {envs_to_delete}")

        if envs_to_delete:
            self._clean_up_environments(conda_cli_runner, envs_to_delete)

        yield
        self._clean_up_environments(conda_cli_runner, ENVIRONMENTS.keys())


    @pytest.mark.parametrize("env_name", ENVIRONMENTS.keys())
    def test_create_environment(self, conda_cli_runner, env_name):
        """Test the creation of a new Conda environment."""
        env_details = ENVIRONMENTS[env_name]

        result = conda_cli_runner.create_conda_env(env_name, env_details["python_version"]).with_json_output().run()
        assert result.returncode == 0, f"Failed to create environment"

        json_output = json.loads(result.stdout)
        assert json_output["prefix"].endswith(env_name), f"Wrong environment path: {json_output['prefix']}"
        assert json_output.get("success", False), f"Environment creation not successful: {json_output}"

    @pytest.mark.parametrize("env_name", ENVIRONMENTS.keys())
    def test_search_packages(self, conda_cli_runner, env_name):
        """Test the search for packages in a Conda environment."""
        env_details = ENVIRONMENTS[env_name]
        for pkg_name, expected_version in env_details["packages"].items():
            search_query = f"{pkg_name}={expected_version}" if expected_version else pkg_name

            result = conda_cli_runner.search_conda_package(search_query).with_json_output().run()
            assert result.returncode == 0, f"Failed to search for package: {pkg_name}"

            results_json = json.loads(result.stdout)

            # Verify the top-level key exists
            assert pkg_name in results_json, f"Package '{pkg_name}' not found in search results"

            records = results_json[pkg_name]
            # Verify there is at least one build
            assert records, f"No builds found for package '{pkg_name}'"

            # Check that all records have the same package name and version (if specified)
            for record in records:
                assert record["name"] == pkg_name, f"Mismatched package name: {record['name']} != {pkg_name}"
                if expected_version is not None:
                    assert record["version"] == expected_version, (
                        f"Unexpected version for {pkg_name}: {record['version']} "
                        f"(expected: {expected_version})"
                    )

    @pytest.mark.parametrize("env_name", ENVIRONMENTS.keys())
    def test_install_packages(self, conda_cli_runner, env_name):
        """Test the installation of packages in a Conda environment."""
        env_details = ENVIRONMENTS[env_name]
        expected_packages = env_details["packages"]

        result = conda_cli_runner.install_conda_packages(env_name, env_details["packages"]).with_json_output().run()
        assert result.returncode == 0, f"Failed to install packages"

        json_output = json.loads(result.stdout)
        linked_packages = json_output.get("actions", {}).get("LINK", [])
        installed_packages = {pkg['name']: pkg['version'] for pkg in linked_packages}

        logger.debug(f"Installed packages: {installed_packages}")

        for pkg_name, expected_version in expected_packages.items():
            assert pkg_name in installed_packages, f"Package '{pkg_name}' not found in installed packages"

            if expected_version is not None:
                actual_version = installed_packages[pkg_name]
                assert actual_version == expected_version, (
                    f"Package '{pkg_name}' version mismatch: expected '{expected_version}', got '{actual_version}'"
                )

    @pytest.mark.parametrize("env_name", ENVIRONMENTS.keys())
    def test_verify_packages(self, conda_cli_runner, env_name):
        """Test the verification of packages in a Conda environment."""
        env_details = ENVIRONMENTS[env_name]

        result = conda_cli_runner.list_conda_packages(env_name).with_json_output().run()
        assert result.returncode == 0, f"Failed to list installed packages"

        json_output = json.loads(result.stdout)
        installed_packages = {package['name']: package['version'] for package in json_output}
        logger.debug(f"Installed packages: {installed_packages}")

        for pkg_name, expected_version in env_details["packages"].items():
            assert pkg_name in installed_packages, f"Package '{pkg_name}' not found in installed packages"

            if expected_version is not None:
                actual_version = installed_packages[pkg_name]
                assert actual_version == expected_version, (
                    f"Version mismatch for {pkg_name}: expected {expected_version}, got {actual_version}"
                )
