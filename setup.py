#!/usr/bin/env python3
"""
Setup script for Auto LinkedIn
"""

import os
from setuptools import setup, find_packages

# Get package info
package_name = "auto_linkedin"
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get version
version = {}
with open(os.path.join(here, package_name, "version.py")) as f:
    exec(f.read(), version)

# Required packages
REQUIRED = [
    "pyqt6>=6.5.0",
    "playwright>=1.30.0",
    "pandas>=1.5.0",
    "openpyxl>=3.1.0",
    "pillow>=9.5.0",
    "pytz>=2023.3",
    "requests>=2.28.0",
    "websockets>=10.4",
]

# Development packages
EXTRAS = {
    "dev": [
        "pytest>=7.3.1",
        "black>=23.3.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.3.0",
    ]
}

setup(
    name=package_name,
    version=version["__version__"],
    description="Python application for LinkedIn automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/auto-linkedin",
    author="Auto LinkedIn",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="linkedin, automation, social media",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.9",
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    entry_points={
        "console_scripts": [
            "auto-linkedin=auto_linkedin.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/yourusername/auto-linkedin/issues",
        "Source": "https://github.com/yourusername/auto-linkedin",
    },
) 