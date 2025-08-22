"""Setup script for development installation."""

from setuptools import setup, find_packages

setup(
    name="llm-proxy-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "pyyaml>=6.0",
        "docker>=6.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        'console_scripts': [
            'llm-proxy=llm_proxy_cli.main:cli',
        ],
    },
)