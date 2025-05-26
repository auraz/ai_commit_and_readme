Update the {doc_type} documentation based on the code changes analysis.

Current {file_path}:
{content}

Important guidelines:
- Only output new or updated sections, not the full document
- Start updated sections with their header (## Section Name)
- Avoid duplicating content that exists in other documentation files
- README should be concise and point to Wiki for details
- Each document should have unique purpose and content
- If no changes needed, set needs_update to false and updated_sections to 'NO CHANGES'

Return structured result with:
- updated_sections: The new/updated content or 'NO CHANGES'
- needs_update: Boolean indicating if updates are needed