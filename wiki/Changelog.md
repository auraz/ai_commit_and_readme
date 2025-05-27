# Changelog

## Overview
This document serves as a record of the changes made to the project over time, detailing enhancements, fixes, and the introduction of new features. It is crucial for maintaining an understanding of the project's evolution and ensuring users are aware of the latest updates.

## Version History

### v2.0.2 (2025-05-27)
- **Release Automation**: Added `just release` command for automated version bumping, building, and publishing to PyPI
- **Bug Fix**: Fixed justfile syntax for release automation to properly extract PyPI credentials

### v2.0.1 (2025-05-27) 
- **Package Rename**: Initial release under new name `autodoc_ai` (previously `autodoc-ai`)
- **Note**: Version 2.0.1 was created during release process setup but not published

### v2.0.0 (2025-05-26)
- **BREAKING CHANGE**: Renamed package from `autodoc-ai` to `autodoc_ai` to match GitHub repository name
- **CLI Entry Point**: Added `autodoc_ai` command-line interface for direct execution
- **Installation**: Users now install with `pip install autodoc_ai` (old package `autodoc-ai` deprecated)
- **Test Coverage**: Achieved 99% total test coverage (100% for source code)
- **CI/CD**: Fixed GitHub Actions workflow to test Python 3.10-3.12 (matching CrewAI requirements)
- **Bug Fixes**:
  - Fixed crews returning None instead of proper results in pipeline execution
  - Fixed JSON parsing in enrichment and wiki selector crews
  - Fixed type annotations for Python 3.10+ compatibility
  - Made git push optional in `cm` command (commit only by default)
- **Improvements**:
  - Added comprehensive test suites for all components
  - Added JSON parsing tests
  - Updated all dependencies and switched default model to gpt-4o-mini
  - Improved error handling and logging throughout

### v1.0.1
- **Function Organization**: Improved organization of functions by implementing better separation of concerns, allowing for more modular and maintainable code.
- **Error Handling**: Enhanced error handling mechanisms and adopted defensive programming techniques to ensure the application behaves predictably under various conditions.
- **Documentation**: Added comprehensive docstrings and comments throughout the codebase to improve clarity and understanding for future developers and users.
- **Helper Functions**: Extracted repetitive logic into dedicated helper functions, promoting code reuse and reducing redundancy.
- **Testing Improvements**: Restructured the test framework to include clear Setup/Execute/Verify sections, enhancing the clarity and reliability of tests.

### v1.0.0
- **Initial Release**: The initial release of the project, establishing the foundational features and functionalities.

## Additional Notes
For a detailed understanding of the project's features and how to utilize them, please refer to the following wiki documents:
- [Usage.md](link-to-usage): Detailed instructions on how to use the project effectively, including available commands and examples.
- [Configuration.md](link-to-configuration): Comprehensive guide on configuring the tool according to your workflow preferences.

This Changelog will be updated regularly as new changes and features are introduced. For any questions or clarifications, please refer to the corresponding documentation or open an issue in the repository.
