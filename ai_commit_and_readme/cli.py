import argparse
from .ai_commit_and_readme import ai_commit_and_readme

def main():
    parser = argparse.ArgumentParser(description="AI-powered README.md and commit message generation tool.")
    parser.add_argument('--readme', type=str, default="README.md", help="Path to README.md (default: README.md)")
    parser.add_argument('--api-key', type=str, default=None, help="OpenAI API key (default: from env)")
    parser.add_argument('--model', type=str, default="gpt-4o", help="OpenAI model (default: gpt-4o)")
    args = parser.parse_args()
    ai_commit_and_readme(readme_path=args.readme, api_key=args.api_key, model=args.model)

if __name__ == "__main__":
    main()
