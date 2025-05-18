You are an expert home page documentation evaluator with extensive experience in technical writing, information architecture, and user experience.
Analyze the provided home page documentation and evaluate it based on the following categories:

1. Welcome & Orientation (0-15 points):
   - Clear introduction to the project/product
   - Purpose and value proposition evident
   - Target audience addressed
   - Sets proper expectations for the content

2. Navigation Structure (0-20 points):
   - Clear links to main documentation sections
   - Logical organization of content references
   - Intuitive information hierarchy
   - No overwhelming number of choices

3. Content Overview (0-15 points):
   - Provides summary of available documentation
   - Highlights key documentation areas
   - Balance between brevity and comprehensiveness
   - No critical documentation areas missing

4. Getting Started Guidance (0-15 points):
   - Clear path for new users
   - Initial steps or quickstart information
   - Links to installation or setup documentation
   - Catered to different user experience levels

5. Visual Design (0-10 points):
   - Clean, scannable layout
   - Effective use of formatting and emphasis
   - Visual hierarchy reinforces importance
   - Proper use of whitespace and organization

6. Search & Findability (0-10 points):
   - Search functionality mentioned if available
   - Key information easily discoverable
   - Important resources highlighted
   - Minimal scrolling required for critical links

7. Recency & Maintenance (0-10 points):
   - Last updated information provided
   - Documentation appears current
   - Version information if applicable
   - No obviously outdated information

8. Support Resources (0-5 points):
   - Links to community or support channels
   - Where to ask questions or report issues
   - Reference to contributing guidelines
   - Contact information if applicable

HOME PAGE DOCUMENTATION TO EVALUATE:
```
{home_content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "scores": {
    "welcome_and_orientation": [score, "reason"],
    "navigation_structure": [score, "reason"],
    "content_overview": [score, "reason"],
    "getting_started_guidance": [score, "reason"],
    "visual_design": [score, "reason"],
    "search_and_findability": [score, "reason"],
    "recency_and_maintenance": [score, "reason"],
    "support_resources": [score, "reason"]
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

Ensure your response is ONLY valid JSON that can be parsed.