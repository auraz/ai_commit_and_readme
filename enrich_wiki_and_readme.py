import sys
from pathlib import Path

# Usage: python enrich_wiki_and_readme.py <section> <enrichment_file> <wiki_file> <readme_file> <wiki_url>
# Example: python enrich_wiki_and_readme.py Usage new_usage.md wiki/Usage.md README.md https://github.com/auraz/ai_commit_and_readme/wiki/Usage

def update_wiki(wiki_file, enrichment_text):
    wiki_path = Path(wiki_file)
    content = wiki_path.read_text(encoding='utf-8')
    # Simple append; customize as needed
    content += f"\n\n---\n\n{enrichment_text}\n"
    wiki_path.write_text(content, encoding='utf-8')

def update_readme(readme_file, section, summary, wiki_url):
    readme_path = Path(readme_file)
    content = readme_path.read_text(encoding='utf-8')
    # Replace or insert section with summary and link
    import re
    pattern = rf"## {section}.*?(?=## |\Z)"
    replacement = f"## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
    new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if n == 0:
        # Section not found, append at end
        new_content = content + f"\n## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
    readme_path.write_text(new_content, encoding='utf-8')

def main():
    if len(sys.argv) != 6:
        print("Usage: python enrich_wiki_and_readme.py <section> <enrichment_file> <wiki_file> <readme_file> <wiki_url>")
        sys.exit(1)
    section, enrichment_file, wiki_file, readme_file, wiki_url = sys.argv[1:6]
    enrichment_text = Path(enrichment_file).read_text(encoding='utf-8')
    # For README, use the first paragraph as summary
    summary = enrichment_text.strip().split('\n\n')[0]
    update_wiki(wiki_file, enrichment_text)
    update_readme(readme_file, section, summary, wiki_url)
    print(f"Updated {wiki_file} and {readme_file} for section '{section}'.")

if __name__ == "__main__":
    main()
