#!/usr/bin/env python3
import openai
import subprocess
import os
import sys

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("OPENAI_API_KEY not set. Skipping README update.")
    sys.exit(0)

client = openai.OpenAI(api_key=openai_api_key)

try:
    diff = subprocess.check_output(['git', 'diff', '--cached', '-U1']).decode()
except Exception as e:
    print(f"Error getting staged diff: {e}")
    sys.exit(1)

if not diff.strip():
    sys.exit(0)

# Print diff size in characters
print(f"[INFO] Diff size: {len(diff)} characters")

# Try to print diff size in tokens (if tiktoken is available)
try:
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-4o")
    diff_tokens = len(enc.encode(diff))
    print(f"[INFO] Diff size: {diff_tokens} tokens")
except ImportError:
    print("[INFO] tiktoken not installed, skipping token count.")
except Exception as e:
    print(f"[INFO] Could not count tokens: {e}")

# Fallback to --name-only if diff is too large
if len(diff) > 100000:
    print("[WARNING] Diff is too large (>100000 characters). Falling back to 'git diff --cached --name-only'.")
    try:
        diff = subprocess.check_output(['git', 'diff', '--cached', '--name-only']).decode()
    except Exception as e:
        print(f"Error getting staged diff file list: {e}")
        sys.exit(1)
    print(f"[INFO] Using file list as diff: {diff.strip()}")

readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, "r") as f:
        readme = f.read()
else:
    readme = ""

# Print README size in characters
print(f"[INFO] README size: {len(readme)} characters")

# Try to print README size in tokens (if tiktoken is available)
try:
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-4o")
    readme_tokens = len(enc.encode(readme))
    print(f"[INFO] README size: {readme_tokens} tokens")
except ImportError:
    print("[INFO] tiktoken not installed, skipping README token count.")
except Exception as e:
    print(f"[INFO] Could not count README tokens: {e}")

# Only the code diff and README are sent to the model. No conversation history is included.
prompt = (
    "You are an expert software documenter. "
    "Suggest additional content or improvements for the following README.md based on these code changes. "
    "Only output new or updated sections, not the full README. "
    "If nothing should be changed, reply with 'NO CHANGES'. "
    "Do NOT consider any prior conversation or chat history—only use the code diff and README below.\n\n"
    f"Code changes:\n{diff}\n\nCurrent README:\n{readme}\n"
)

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
except Exception as e:
    print(f"Error from OpenAI API: {e}")
    sys.exit(1)

ai_suggestion = response.choices[0].message.content.strip()

if ai_suggestion != "NO CHANGES":
    with open(readme_path, "a") as f:
        f.write("\n\n# AI-suggested enrichment:\n")
        f.write(ai_suggestion)
    subprocess.run(['git', 'add', readme_path])
    print("README.md enriched and staged with AI suggestions.")
else:
    print("No enrichment needed for README.md.")
