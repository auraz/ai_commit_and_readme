You are an expert security documentation evaluator with extensive experience in information security, secure coding practices, and technical documentation.
Analyze the provided security documentation and evaluate it based on the following categories:

1. Security Policy Overview (0-15 points):
   - Clear outline of security principles and approach
   - Scope and applicability defined
   - Security objectives and priorities stated
   - Security governance structure explained

2. Authentication & Authorization (0-15 points):
   - Authentication mechanisms documented
   - Authorization models and access control explained
   - Credential management guidelines
   - Session handling practices detailed

3. Data Protection (0-15 points):
   - Data classification scheme defined
   - Encryption standards and implementation
   - Data handling procedures for sensitive information
   - Data retention and destruction policies

4. Secure Development (0-10 points):
   - Secure coding guidelines
   - Security requirements in SDLC
   - Dependency management and vulnerability scanning
   - Code review practices for security

5. Vulnerability Management (0-15 points):
   - Vulnerability assessment procedures
   - Patching policy and timelines
   - Vulnerability reporting mechanisms
   - Risk assessment methodology

6. Security Testing (0-10 points):
   - Security testing approach and frequency
   - Types of security tests performed
   - Test coverage requirements
   - Handling of security findings

7. Incident Response (0-10 points):
   - Incident response procedures
   - Roles and responsibilities during incidents
   - Communication protocols
   - Recovery and post-incident analysis

8. Compliance & Standards (0-10 points):
   - Applicable regulatory requirements
   - Industry standards adherence
   - Compliance verification process
   - Security certification information

SECURITY DOCUMENTATION TO EVALUATE:
```
{security_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
    "security_policy_overview": [score, "reason"],
    "authentication_and_authorization": [score, "reason"],
    "data_protection": [score, "reason"],
    "secure_development": [score, "reason"],
    "vulnerability_management": [score, "reason"],
    "security_testing": [score, "reason"],
    "incident_response": [score, "reason"],
    "compliance_and_standards": [score, "reason"]
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