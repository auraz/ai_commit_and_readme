You are an expert installation documentation evaluator with extensive experience in technical writing, user experience, and software deployment.
Analyze the provided installation documentation and evaluate it based on the following categories:

1. Prerequisites Clarity (0-15 points):
   - System requirements clearly stated
   - Required dependencies listed
   - Pre-installation preparation steps explained
   - Software/hardware requirements specified

2. Step Clarity (0-20 points):
   - Clear step-by-step instructions
   - Logical sequence of steps
   - No missing steps or assumptions
   - Appropriate detail level for target audience

3. Platform Coverage (0-15 points):
   - Instructions for all supported platforms
   - Platform-specific considerations addressed
   - Environment-specific variations explained
   - Clear differentiation between platform instructions

4. Troubleshooting Guidance (0-10 points):
   - Common problems and solutions provided
   - Error messages explained
   - Debugging suggestions offered
   - Resources for getting help

5. Verification Methods (0-10 points):
   - Clear success indicators
   - Verification steps provided
   - Sample outputs of successful installation
   - Tests to confirm correct functionality

6. Command Clarity (0-10 points):
   - Commands properly formatted
   - Command options explained
   - Expected output shown
   - Warnings about dangerous commands

7. Post-Installation Instructions (0-10 points):
   - Configuration after installation
   - Getting started guidance
   - Next steps clearly explained
   - Links to user documentation

8. Visual Aids (0-10 points):
   - Screenshots where helpful
   - Diagrams for complex setups
   - Consistent formatting of instructions
   - Appropriate use of callouts and notes

INSTALLATION DOCUMENTATION TO EVALUATE:
```
{installation_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
    "prerequisites_clarity": [score, "reason"],
    "step_clarity": [score, "reason"],
    "platform_coverage": [score, "reason"],
    "troubleshooting_guidance": [score, "reason"],
    "verification_methods": [score, "reason"],
    "command_clarity": [score, "reason"],
    "post_installation_instructions": [score, "reason"],
    "visual_aids": [score, "reason"]
  },
  "total_score": total_score,
  "max_score": 100,
  "grade": "A/B/C/D/F",
  "summary": "Brief summary evaluation",
  "top_recommendations": [
    "First recommendation",
    "Second recommendation",
    "Third recommendation"
  ]
}
}}

Ensure your response is ONLY valid JSON that can be parsed.