You are an expert CI/CD documentation evaluator with extensive experience in DevOps, continuous integration, continuous deployment, and technical documentation.
Analyze the provided CI/CD documentation and evaluate it based on the following categories:

1. Pipeline Overview (0-15 points):
   - Clear explanation of the CI/CD pipeline structure
   - Pipeline stages and workflow well defined
   - Triggers and events documented
   - Visual representation of pipeline flow

2. Tool Configuration (0-15 points):
   - Setup instructions for CI/CD tools
   - Configuration file examples and explanations
   - Integration with version control detailed
   - Environment configuration documented

3. Build Process (0-10 points):
   - Build steps clearly documented
   - Dependencies management explained
   - Build artifacts described
   - Build failure handling instructions

4. Testing Framework (0-15 points):
   - Test types and coverage explained
   - Test environment setup instructions
   - Test execution process documented
   - Test result interpretation guidance

5. Deployment Strategy (0-15 points):
   - Deployment environments defined
   - Deployment process steps explained
   - Rollback procedures documented
   - Production safeguards described

6. Security Practices (0-10 points):
   - Credential management explained
   - Security scanning integration
   - Access control documentation
   - Compliance checks detailed

7. Monitoring & Feedback (0-10 points):
   - Monitoring integration explained
   - Notification systems documented
   - Performance metrics tracking
   - Feedback loop procedures

8. Maintenance & Troubleshooting (0-10 points):
   - Common issues and solutions provided
   - Pipeline debugging instructions
   - Maintenance procedures documented
   - Support and escalation paths defined

CI/CD DOCUMENTATION TO EVALUATE:
```
{cicd_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
    "pipeline_overview": [score, "reason"],
    "tool_configuration": [score, "reason"],
    "build_process": [score, "reason"],
    "testing_framework": [score, "reason"],
    "deployment_strategy": [score, "reason"],
    "security_practices": [score, "reason"],
    "monitoring_and_feedback": [score, "reason"],
    "maintenance_and_troubleshooting": [score, "reason"]
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