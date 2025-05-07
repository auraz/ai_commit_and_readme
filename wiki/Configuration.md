# Configuration

This project can be configured using environment variables and optional configuration files.

## Environment Variables

- `OPENAI_API_KEY`: API key for the OpenAI service. Required for AI-powered features.
- `AICOMMIT_API_KEY`: API key for the aicommit service (if different from OpenAI).
- `AICOMMIT_CONFIG_PATH`: Path to a custom configuration file (optional).

## Error Handling

- If the `OPENAI_API_KEY` is not set or is incorrect, the program will exit gracefully with an error message.
- If the specified README file does not exist, the program will default to an empty string and continue execution.

## Example

- `AICOMMIT_API_KEY`: API key for the AI service
- `AICOMMIT_CONFIG_PATH`: Path to custom configuration file
