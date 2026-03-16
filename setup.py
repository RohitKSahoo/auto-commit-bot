from setuptools import setup

setup(
    name="autocommitbot",
    version="1.0",
    py_modules=["cli"],
    install_requires=["typer", "rich"],
    entry_points={
        "console_scripts": [
            "autocommit=cli:app",
        ],
    },
)