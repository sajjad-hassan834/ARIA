from setuptools import setup, find_packages

setup(
    name="aria-common",
    version="1.0.0",
    description="Global common modules, configs, models and utilities for ARIA system",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
)
