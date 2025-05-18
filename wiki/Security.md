# Security Best Practices

This guide outlines security best practices for working with the `ai_commit_and_readme` tool, particularly regarding API key management and sensitive information.

## API Key Management

The `ai_commit_and_readme` tool requires an OpenAI API key to function. Proper API key management is essential to prevent unauthorized access and potential abuse.

### DO:

- Store your OpenAI API key as an environment variable
- Use a `.env` file that is excluded from version control
- Rotate your API keys periodically
- Use different API keys for development and production
- Consider using API key management services for team environments

### DON'T:

- Hardcode API keys in your code
- Include API keys in version control
- Share API keys in public forums or chat applications
- Use the same API key across multiple projects or environments
- Log API keys in application logs

## Environment Variables

### Setting Environment Variables

#### Linux/macOS

```bash
# Temporary (session only)
export OPENAI_API_KEY="your-api-key"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows

```powershell
# Temporary (session only)
$env:OPENAI_API_KEY="your-api-key"

# Permanent (System Settings)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-api-key", "User")
```

### Using .env Files

1. Create a `.env` file in your project root:
   ```
   OPENAI_API_KEY=your-api-key
   ```

2. Ensure `.env` is listed in your `.gitignore` file:
   ```
   # .gitignore
   .env
   ```

3. Create a `.env.example` file with placeholder values to help others set up their environment:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

## Token Management

API keys often work with usage-based pricing. Consider implementing:

- Rate limiting to prevent accidental overuse
- Usage monitoring to track consumption
- Alert mechanisms for unusual activity
