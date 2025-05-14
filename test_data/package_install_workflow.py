ENVIRONMENTS = {
    "py311": {
        "description": "Python 3.11 with numpy and pytorch",
        "python_version": "3.11",
        "packages": {
            "numpy": "2.1.1",
            "pytorch": "2.3.1"
        }
    },
    "py313": {
        "description": "Python 3.13 with pytest, requests and pandas",
        "python_version": "3.13",
        "packages": {
            "pytest": None, # install latest
            "requests": "2.32.3",
            "pandas": "2.2.3"
        }
    }
}