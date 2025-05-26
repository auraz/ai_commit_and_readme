# Architecture

This document provides an overview of the architecture for the `autodoc_ai` tool, explaining how the various components work together.

## System Overview

`autodoc_ai` is designed with a modular architecture that follows the single responsibility principle. The system processes git repository information, sends it to OpenAI's API, and formats the results for user consumption.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│ Git Content │ ──► │ Text         │ ──► │ OpenAI API  │ ──► │ Formatted   │
│ Extraction  │     │ Processing   │     │ Interaction │     │ Output      │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
```

## Core Components

### 1. CLI Interface

The entry point for the application, responsible for:
- Parsing command-line arguments
- Validating user input
- Orchestrating the workflow
- Providing feedback to the user

### 2. Git Content Extraction

Interfaces with the git repository to:
- Extract changes between commits
- Read file contents
- Determine what has been added, modified, or deleted
- Handle different file paths and encodings

### 3. Text Processing Pipeline

Processes extracted text using a pipeline pattern:
- Filters out non-relevant content
- Truncates content to stay within token limits
- Organizes content for optimal prompt structure
- Manages different file types appropriately

### 4. OpenAI API Client

Manages communication with the OpenAI API:
- Handles authentication
- Constructs appropriate prompts
- Sends requests with proper parameters
- Processes API responses
- Implements error handling and retries

### 5. Output Formatter

Transforms API responses into the final output:
- Formats markdown content
- Applies consistent styling
- Handles escape characters
- Writes to the appropriate output destination

## Data Flow

1. **Input Collection**: CLI arguments and git repository state
2. **Content Extraction**: Repository content is read and processed
3. **Prompt Construction**: Content is formatted into prompt templates
4. **API Request**: Prompt is sent to OpenAI API
5. **Response Processing**: API response is parsed and validated
6. **Output Generation**: Formatted README or commit message is produced

## Design Patterns

### Pipeline Pattern

The core processing logic uses the pipeline pattern (implemented with `pipetools`) to create a series of transformations that data flows through. This allows for:
- Clear separation of concerns
- Testability of individual steps
- Easy addition of new processing steps
- Functional programming style

```
extract_content >> filter_content >> truncate_to_token_limit >> format_prompt >> call_api >> format_response
```

### Dependency Injection

Key components are designed with dependency injection to facilitate:
- Testing with mock dependencies
- Configuration changes without code modification
- Clearer separation of responsibilities

### Factory Pattern

Used for creating different types of processors based on file types or processing needs.

## Code Organization

### Package Structure

```
autodoc_ai/
├── __init__.py           # Package initialization
├── cli.py                # Command-line interface
├── config.py             # Configuration management
├── content_extractor.py  # Git content extraction
├── openai_client.py      # OpenAI API interaction
├── pipeline/             # Pipeline components
│   ├── __init__.py
│   ├── filters.py        # Content filtering
│   ├── formatters.py     # Output formatting
│   └── processors.py     # Text processing
├── prompt.md             # Prompt template
└── utils/                # Utility functions
    ├── __init__.py
    ├── git.py            # Git-related utilities
    ├── logging.py        # Logging utilities
    └── token_counter.py  # Token counting for OpenAI
```

## External Dependencies

- **openai**: Core API client for OpenAI services
- **tiktoken**: Token counting for prompt optimization
- **rich**: Terminal output formatting and styling
- **pipetools**: Functional pipeline construction

## Error Handling

The application implements a comprehensive error handling strategy:
- Graceful degradation when services are unavailable
- User-friendly error messages
- Detailed logging for debugging
- Recovery mechanisms where possible

## Configuration Management

Configuration is managed through:
- Environment variables (OPENAI_API_KEY)
- Command-line arguments
- Default configurations for prompt templates

## Testing Strategy

The architecture supports a comprehensive testing approach:
- Unit tests for individual components
- Integration tests for component interactions
- Mock objects for external dependencies
- Test fixtures for common test scenarios
