#!/usr/bin/env python3
"""
Setup script for eval_engine package.
"""

from setuptools import setup, find_packages

setup(
    name="eval_engine",
    version="0.1.0",
    description="Closed-loop evaluation and improvement system for documentation",
    author="AI Commit and README Team",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.0.0",
        "numpy>=1.19.0",
    ],
    entry_points={
        "console_scripts": [
            "eval-engine=eval_engine.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
)