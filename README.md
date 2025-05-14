# Conda CLI Test Automation Framework

## Overview

This lightweight framework automates the creation of [Conda](https://docs.conda.io/en/latest/) environments, searching for and installing packages with version control, and validating installations using Python and Pytest. It is cross-platform (Linux, macOS, Windows) and includes structured logging and optional HTML reporting.

Each environment is created, validated, and cleaned up automatically before and after each test class, ensuring test isolation and repeatability. To ensure robust and reliable parsing, the `--json` flag is used with applicable **Conda** commands instead of relying on stdout string parsing.

This project focuses on simplicity and clarity in Conda CLI testing. A more robust and extensible framework structure with package management, linters, pre-commit hooks, extended logging, and tagging is implemented in the second project - [api-test-automation-framework](https://github.com/heksein/api-test-automation-framework).

## Project Structure

```bash
conda-cli-test-automation/
├── test_data/
│   └── package_install_workflow.py        # Conda environments and packages definition
│
├── utils/
│   └── conda_cli_runner.py                # Fluent, safe Conda CLI wrapper
│
├── tests/
│   ├── conftest.py                        # Global pytest fixtures
│   └── test_package_install_workflow.py   # Parametrized functional tests
│
├── .gitignore
├── pytest.ini                             # Pytest and logging configuration
├── requirements.txt
└── README.md
```

## Features

* Cross-platform support (Linux, macOS, Windows)
* Parametrized, data-driven testing with per-package versioning
* Clean modular structure for CLI interaction and test logic
* Logging and test reporting (`pytest-html` support)
* Automatic environment cleanup before and after test execution

## Getting Started

### Requirements

* Python 3.11+
* [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) must be installed and available in PATH

### Install dependencies

Once all requirements are met, we need to:

1. Create virtual environment:

    ```bash
    python -m venv .venv
    ```

2. Activate venv depending on platform:

    On **macOS**/**Linux** just run the following:

    ```bash
    source .venv/bin/activate
    ```

    On **Windows** (recommended to use **Anaconda Prompt**) execute:

    ```bash
    .venv\Scripts\activate.bat
    ```

3. Install the dependencies from the **requirements.txt** file:

    ```bash
    pip install -r requirements.txt
    ```

### Run Tests

To run all tests, navigate to the project root dir and execute:

```bash
pytest
```

To run specic test:

```bash
pytest -k test_create_environment
```

To generate test reports:

```bash
# JUnit XML (for CI)
pytest --junitxml=report/results.xml

# HTML report (for manual review)
pytest --html=report/report.html
```

## Logging

This project uses Python’s built-in logging module to log Conda commands and other information during test execution. By default, logs are shown in the terminal (CLI). But in case of need, logs can be also written into the file (as I've shown in API test automation framework) by adding `log_file` options into **pytest.ini**.

You can change the [log verbosity](https://docs.python.org/3/library/logging.html#logging-levels) by modifying the `log_cli_level` in **pytest.ini**.

## Test Data Management

All environments and packages are defined in:

```python
test_data/package_install_workflow.py
```

Example:

```python
ENVIRONMENTS = {
    "py313": {
        "description": "Python 3.13 with pytest, requests and pandas",
        "python_version": "3.13",
        "packages": {
            "pytest": None,  # Install latest version
            "requests": "2.32.3",
            "pandas": "2.2.3"
        }
    }
}
```

You can add more or modify as needed.
