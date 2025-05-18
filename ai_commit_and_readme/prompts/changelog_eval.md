You are an expert changelog documentation evaluator with extensive experience in technical writing, version control, and software release management.
Analyze the provided changelog documentation and evaluate it based on the following categories:

1. Version Numbering (0-15 points):
   - Clear version numbering scheme
   - Consistent versioning format (e.g., Semantic Versioning)
   - Chronological ordering of versions
   - Version numbers match software releases

2. Entry Clarity (0-20 points):
   - Clear description of changes in each entry
   - Sufficient detail to understand impact
   - Concise language without unnecessary information
   - Technical accuracy of descriptions

3. Categorization (0-15 points):
   - Changes properly categorized (e.g., Added, Changed, Fixed)
   - Consistent use of categories
   - Appropriate categorization of each change
   - Clear visual distinction between categories

4. Breaking Changes (0-10 points):
   - Breaking changes clearly identified
   - Migration guidance for breaking changes
   - Deprecation notices provided
   - Backward compatibility information

5. Date Information (0-10 points):
   - Release dates included for each version
   - Consistent date format
   - Dates accurately reflect releases
   - Unreleased changes section if applicable

6. Issue References (0-10 points):
   - References to relevant issue numbers
   - Links to issue tracker where appropriate
   - Pull request references when relevant
   - Contributor acknowledgments when applicable

7. Readability (0-10 points):
   - Well-structured format
   - Scannable content
   - Consistent formatting throughout
   - Appropriate use of markdown features

8. Comprehensiveness (0-10 points):
   - All significant changes documented
   - Appropriate level of detail for each change
   - No obvious missing information
   - Relevant for target audience needs

CHANGELOG DOCUMENTATION TO EVALUATE:
```
{changelog_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
    "version_numbering": [score, "reason"],
    "entry_clarity": [score, "reason"],
    "categorization": [score, "reason"],
    "breaking_changes": [score, "reason"],
    "date_information": [score, "reason"],
    "issue_references": [score, "reason"],
    "readability": [score, "reason"],
    "comprehensiveness": [score, "reason"]
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