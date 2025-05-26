#!/usr/bin/env python3
"""Command-line interface for autodoc_ai."""

import sys

from autodoc_ai.crews.pipeline import PipelineCrew


def main():
    """Run the autodoc_ai pipeline."""
    crew = PipelineCrew()
    result = crew.run()
    
    if not result.get("success"):
        print(f"Enrichment failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    print("✅ Documentation enrichment complete!")


if __name__ == "__main__":
    main()