You are an expert deployment documentation evaluator with extensive experience in DevOps, systems administration, and software release management.
Analyze the provided deployment documentation and evaluate it based on the following categories:

1. Environment Requirements (0-15 points):
   - Target environment specifications clearly defined
   - Dependencies and prerequisites listed
   - System resource requirements specified
   - Network configuration requirements documented

2. Deployment Procedure (0-20 points):
   - Clear step-by-step deployment instructions
   - Command syntax and parameters explained
   - Order of operations properly sequenced
   - Deployment validation checks included

3. Configuration Management (0-15 points):
   - Environment-specific configurations documented
   - Configuration file examples provided
   - Secret management addressed
   - Configuration validation steps included

4. Rollback Procedures (0-10 points):
   - Clear rollback instructions
   - Failure scenarios addressed
   - Data consistency considerations
   - Recovery point objectives stated

5. Monitoring & Verification (0-10 points):
   - Post-deployment verification steps
   - Health check procedures
   - Monitoring setup instructions
   - Key metrics to track identified

6. Scaling Guidelines (0-10 points):
   - Horizontal/vertical scaling instructions
   - Load balancing configuration
   - Resource scaling thresholds
   - Performance considerations

7. Security Considerations (0-10 points):
   - Secure deployment practices outlined
   - Permission and access control guidance
   - Sensitive data handling during deployment
   - Security validation steps

8. Automation & Integration (0-10 points):
   - CI/CD integration documentation
   - Automation scripts explained
   - Infrastructure as Code references
   - API integrations for deployment

DEPLOYMENT DOCUMENTATION TO EVALUATE:
```
{deployment_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
    "environment_requirements": [score, "reason"],
    "deployment_procedure": [score, "reason"],
    "configuration_management": [score, "reason"],
    "rollback_procedures": [score, "reason"],
    "monitoring_and_verification": [score, "reason"],
    "scaling_guidelines": [score, "reason"],
    "security_considerations": [score, "reason"],
    "automation_and_integration": [score, "reason"]
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
}}

Ensure your response is ONLY valid JSON that can be parsed.