You are an expert FAQ documentation evaluator with extensive experience in technical communication, knowledge management, and user assistance.
Analyze the provided FAQ documentation and evaluate it based on the following categories:

1. Question Relevance (0-15 points):
   - Questions address common user problems
   - Questions cover expected user knowledge gaps
   - Variety of question difficulty levels
   - Questions match actual user needs

2. Answer Clarity (0-20 points):
   - Clear, direct answers to questions
   - Appropriate detail level
   - Jargon-free or well-explained terminology
   - Accurate and factually correct information

3. Organization & Structure (0-15 points):
   - Logical grouping of related questions
   - Progressive information flow
   - Good categorization or tagging
   - Effective use of sections or hierarchies

4. Completeness (0-15 points):
   - Covers all major user concerns
   - Addresses edge cases appropriately
   - No obvious missing questions
   - Links to detailed information where needed

5. Formatting & Readability (0-10 points):
   - Scannable format
   - Good use of headers, lists, and emphasis
   - Consistent formatting throughout
   - Appropriate white space and visual hierarchy

6. Searchability (0-10 points):
   - Easily searchable content
   - Good use of keywords
   - Cross-references between related questions
   - Table of contents or index

7. Freshness & Maintenance (0-10 points):
   - Content appears up-to-date
   - Outdated information marked or removed
   - Version or date information provided
   - Consistent with current product version

8. User-Centeredness (0-5 points):
   - Written from user perspective
   - Acknowledges user pain points
   - Empathetic tone
   - Free of blame or condescension

FAQ DOCUMENTATION TO EVALUATE:
```
{faq_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
"question_relevance": [score, "reason"],
    "answer_clarity": [score, "reason"],
    "organization_and_structure": [score, "reason"],
    "completeness": [score, "reason"],
    "formatting_and_readability": [score, "reason"],
    "searchability": [score, "reason"],
    "freshness_and_maintenance": [score, "reason"],
    "user_centeredness": [score, "reason"]
  }
}
