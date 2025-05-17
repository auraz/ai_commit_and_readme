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

## Git Security

### Sensitive Information in Repositories

If you accidentally commit sensitive information:

1. Immediately invalidate/rotate the exposed credentials
2. Remove the sensitive data with:
   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch PATH-TO-FILE-WITH-SENSITIVE-DATA" \
   --prune-empty --tag-name-filter cat -- --all
   ```
3. Force-push the cleaned history:
   ```bash
   git push origin --force --all
   ```

### Pre-commit Hooks

Use pre-commit hooks to prevent accidental commits of sensitive information:

```bash
pip install pre-commit
```

Create a `.pre-commit-config.yaml` file:
```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: detect-private-key
    -   id: detect-aws-credentials
```

## Secure Development Practices

- Keep all dependencies updated to avoid known vulnerabilities
- Use minimal permissions when setting up API keys
- Monitor security advisories for all dependencies
- Consider regular security audits for production deployments

## Code Review Checklist

When reviewing code that interacts with APIs or sensitive data:

- [ ] No hardcoded credentials
- [ ] Environment variables used for all sensitive values
- [ ] No sensitive data logged to console or files
- [ ] Error messages do not reveal sensitive implementation details
- [ ] Use secure methods to transmit secrets when deploying

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OpenAI API Usage Policies](https://platform.openai.com/docs/usage-policies)
- [GitHub's Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Twelve-Factor App: Config](https://12factor.net/config)