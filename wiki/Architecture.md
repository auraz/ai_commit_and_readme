# Architecture

This document outlines the architectural design of the `ai_commit_and_readme` project, focusing on the core components and their interactions.

## Overview

The `ai_commit_and_readme` tool uses a functional pipeline pattern to process changes in a repository, analyze them with AI, and generate relevant content for README and wiki files. The tool is built with maintainability, testability, and extensibility in mind.

## Core Architecture

### Pipeline Pattern

The application uses the `pipetools` library to implement a functional pipeline. This pattern:

- Treats functions as data transformers in a sequence
- Passes a context dictionary through the pipeline
- Enables clean composition of functions using the pipe operator (`|`)
- Makes the data flow explicit and traceable

### Context Dictionary

All functions in the pipeline operate on a shared context dictionary (`CtxDict`):

```python
CtxDict = dict[str, Any]
```

This dictionary stores:
- Configuration values
- Git diff data
- File contents
- AI suggestions
- Processing state

Each function in the pipeline receives the context, modifies it, and returns the updated context to the next function.

## Pipeline Flow

The main pipeline in `enrich()` executes these operations in sequence:

1. **Initialization**: Sets up the context with default values
2. **API Key Verification**: Ensures the OpenAI API key is available
3. **Diff Retrieval**: Gets the staged git diff
4. **Validation**: Checks if there are changes to process
5. **Analysis**: Processes the diff and gathers information
6. **File Reading**: Reads README and wiki files
7. **AI Processing**: Gets suggestions for content enrichment
8. **Content Writing**: Updates files with AI suggestions
9. **Git Staging**: Stages the updated files

## Key Components

### Function Decorators

The `ensure_initialized` decorator wraps pipeline functions to guarantee the context is properly initialized before execution:

```python
def ensure_initialized(func: Callable) -> PipeFunction:
    def wrapper(ctx: CtxDict) -> CtxDict:
        ctx = initialize_context(ctx)
        return func(ctx)
    return wrapper
```

### Function Factory Pattern

Many functions use a factory pattern to create parametrized pipeline steps:

```python
def get_file(file_key: str, path_key: str):
    """Factory function creating a pipeline step to read a file."""
    def _get_file(ctx: CtxDict) -> CtxDict:
        path = ctx[path_key]
        with open(path, encoding="utf-8") as f:
            ctx[file_key] = f.read()
        return ctx
    return ensure_initialized(_get_file)
```

### Helper Functions

Specialized helper functions extract common functionality:

- `extract_ai_content`: Safely extracts content from AI API responses
- `_update_with_section_header`: Handles section-based content updates

## Pipeline Definition and Execution

The main pipeline is defined using the pipe operator for enhanced readability:

```python
enrichment_pipeline = (
    pipe
    | initialize_context
    | check_api_key
    | get_diff()
    | check_diff_empty
    | print_diff_info
    | fallback_large_diff
    | read_readme
    | print_readme_info
    | select_wiki_articles
    | enrich_readme()
    | get_selected_wiki_files
    | print_selected_wiki_files
    | enrich_selected_wikis
    | write_enrichment_outputs
)

# Execute the pipeline with an empty initial context
enrichment_pipeline({})
```

## Testing Architecture

The testing approach follows these principles:

1. **Unit Testing**: Each function is tested in isolation
2. **Mock Dependencies**: External dependencies are mocked
3. **Structured Tests**: Tests follow the Setup/Execute/Verify pattern
4. **Pipeline Testing**: The pipeline composition is tested independently

Test helper functions like `make_ctx()` create consistent test contexts.

## Error Handling

The pipeline implements defensive programming with:

- Graceful early exits when prerequisites aren't met
- Safe extraction of data from API responses
- Proper error reporting through logging
- Context preservation even when errors occur

## Extensibility

The architecture enables easy extension through:

1. **Adding Pipeline Steps**: New functions following the context pattern can be inserted
2. **Function Composition**: Complex operations can be composed from simpler ones
3. **Context Enrichment**: The context dictionary can be extended with new data
4. **Alternative Implementations**: Pipeline functions can be swapped out for alternatives

## Optimizations

Several optimizations improve the efficiency of the pipeline:

1. **Context Copying**: Strategic context copying prevents unintended side effects
2. **Helper Extraction**: Common operations are extracted to minimize code duplication
3. **Defensive Access**: Defensive patterns for accessing properties reduce errors
4. **Function Factories**: Parameterized functions reduce repetition

This architecture provides a solid foundation for extending the project with new features while maintaining code quality and testability.