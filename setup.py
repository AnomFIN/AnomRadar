"""Setup script for AnomRadar v2"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="anomradar",
    version="2.0.0",
    author="AnomFIN",
    author_email="info@anomfin.fi",
    description="Production-Ready CLI/TUI Security Scanner Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AnomFIN/AnomRadar",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "anomradar": [
            "reports/*.html",
            "tui/*.txt",
        ],
    },
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "anomradar=anomradar.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.8",
    keywords="security scanner osint reconnaissance passive-scanning",
    project_urls={
        "Bug Reports": "https://github.com/AnomFIN/AnomRadar/issues",
        "Source": "https://github.com/AnomFIN/AnomRadar",
    },
)
