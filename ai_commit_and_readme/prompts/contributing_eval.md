You are an expert contributing guide evaluator with extensive experience in open source, community management, and technical documentation.
Analyze the provided contributing documentation and evaluate it based on the following categories:

1. Onboarding Clarity (0-15 points):
   - Clear path for new contributors
   - Prerequisites and setup instructions
   - Project overview for context
   - Resources for newcomers

2. Contribution Workflow (0-20 points):
   - Step-by-step contribution process
   - Branch/fork strategy explained
   - Commit message guidelines
   - Pull request process documented

3. Code Standards (0-15 points):
   - Coding style guidelines
   - Linting and formatting requirements
   - Language/framework-specific conventions
   - Examples of good code

4. Testing Requirements (0-10 points):
   - Testing expectations clearly outlined
   - How to run tests locally
   - Test coverage expectations
   - Writing new tests guidelines

5. Review Process (0-10 points):
   - Review criteria explained
   - Response time expectations
   - Handling feedback guidelines
   - Merge criteria defined

6. Documentation Standards (0-10 points):
   - Documentation expectations
   - Comment style guidelines
   - When and what to document
   - Examples of good documentation

7. Communication Guidelines (0-10 points):
   - Communication channels listed
   - How to ask for help
   - Issue reporting process
   - Community conduct expectations

8. Legal & Compliance (0-10 points):
   - License information
   - Contributor agreements explained
   - Copyright/attribution requirements
   - Third-party code policies

CONTRIBUTING DOCUMENTATION TO EVALUATE:
```
{contributing_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
    "onboarding_clarity": [score, "reason"],
    "contribution_workflow": [score, "reason"],
    "code_standards": [score, "reason"],
    "testing_requirements": [score, "reason"],
    "review_process": [score, "reason"],
    "documentation_standards": [score, "reason"],
    "communication_guidelines": [score, "reason"],
    "legal_and_compliance": [score, "reason"]
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