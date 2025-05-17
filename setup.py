from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai_commit_and_readme",
    version="1.0.2",
    description="AI-powered README.md and commit message generation tool using OpenAI",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important for Markdown rendering on PyPI
    author="Oleksandr Kryklia",
    author_email="kryklia@gmail.com",
    packages=find_packages(),
    package_data={"ai_commit_and_readme": ["prompt.md"]},
    include_package_data=True,
    install_requires=["openai>=1.0.0", "tiktoken>=0.5.1"],
    entry_points={"console_scripts": ["ai-commit-and-readme=ai_commit_and_readme.cli:main"]},
    python_requires=">=3.7",
    license="MIT",
)
