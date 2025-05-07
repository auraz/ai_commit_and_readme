from setuptools import setup, find_packages

setup(
    name="ai_commit_and_readme",
    version="0.1.0",
    description="AI-powered README.md and commit message generation tool using OpenAI",
    author="Oleksandr Kryklia",
    author_email="kryklia@gmail.com",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "tiktoken>=0.5.1"
    ],
    entry_points={
        "console_scripts": [
            "ai-commit-and-readme=ai_commit_and_readme.main:main"
        ]
    },
    python_requires=">=3.7",
    license="MIT",
)
