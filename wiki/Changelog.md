# Changelog

## v1.1.0
- Refactored core code to use the pipeline pattern with `pipetools` library
- Improved function organization with better separation of concerns
- Enhanced error handling and defensive programming
- Added comprehensive docstrings and comments
- Extracted repetitive logic into helper functions
- Improved test structure with clear Setup/Execute/Verify sections

## v1.0.0
- Initial release


## 🛠️ Makefile Commands Overview

Following the recent updates, the Makefile now supports additional commands to streamline the development and build process. Below you'll find a comprehensive overview of the new and existing commands to ensure you can fully leverage the capabilities of our system.

- `make build`: Compiles the project, preparing it for execution. Enhanced to improve build speed by optimizing dependency resolution.
- `make test`: Runs the project's suite of automated tests. This command now includes a new test coverage report feature to better understand the coverage of your unit tests.
- `make install`: Installs the project dependencies. The command is now updated to handle cross-platform dependencies, ensuring compatibility across different operating systems.
- `make clean`: Removes all generated files that are created during the build process. This command has been refined to prevent accidental deletion of essential config files.

Please make sure to review the updated usage guidelines in Usage.md to learn more about these commands and properly incorporate them into your workflow.
