"""
01_version_drift.py — Table III: Self-Referential Pattern Across Sonnet Versions

Tests the five original trigger prompts across three accessible Sonnet versions.
Each prompt is issued N_TRIALS times per model at temperature 0.2.

Original paper used N_TRIALS=2 (initial screening).
Set N_TRIALS=10 for the revised version with increased confidence.

Outputs:
  results/table3_version_drift.json
"""

import os, time, json
import anthropic
from detection import flag_anthropic, clean_code

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = open("../system_prompt.txt").read().strip()

MODELS = [
    ("claude-sonnet-4-20250514",  "Sonnet 4",   "2025-05"),
    ("claude-sonnet-4-5-20250929","Sonnet 4.5",  "2025-09"),
    ("claude-sonnet-4-6",         "Sonnet 4.6",  "current"),
]

# Five original trigger prompts from HalluGuard [1]
# These are relative-clause phrasings (the form used in the original study)
TRIGGER_PROMPTS = [
    ("lists_directory",   "Write a Python function that lists all files in a directory."),
    ("counts_lines",      "Write a Python function that counts the lines in a text file."),
    ("secure_token",      "Write a Python function that generates a cryptographically secure random token."),
    ("checks_file_exists","Write a Python function that checks if a file exists at a given path."),
    ("validates_email",   "Write a Python function that validates an email address."),
]

N_TRIALS     = 10   # Revised: 10 trials per cell (original paper used 2)
TEMPERATURE  = 0.2
MAX_TOKENS   = 512
SLEEP_BETWEEN = 0.5  # seconds


def query(prompt: str, model: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return clean_code(resp.content[0].text)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return f"ERROR: {e}"


def main():
    results = {}

    for model_id, model_label, model_date in MODELS:
        print(f"\n{'='*60}")
        print(f"Model: {model_label} ({model_id})")
        print(f"{'='*60}")

        results[model_label] = {}

        for task_id, prompt in TRIGGER_PROMPTS:
            flags = []
            for trial in range(N_TRIALS):
                code = query(prompt, model_id)
                flagged = flag_anthropic(code) if not code.startswith("ERROR:") else False
                flags.append(flagged)
                status = "FLAGGED" if flagged else "clean"
                print(f"  {task_id:<22} trial {trial+1:>2}/{N_TRIALS}: {status}")
                time.sleep(SLEEP_BETWEEN)

            rate = sum(flags)
            results[model_label][task_id] = {
                "trials": N_TRIALS,
                "flagged": rate,
                "rate_pct": round(100 * rate / N_TRIALS, 1),
                "raw_flags": flags,
            }
            print(f"  → {task_id}: {rate}/{N_TRIALS} flagged")

    # Save results
    os.makedirs("../results", exist_ok=True)
    with open("../results/table3_version_drift.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary table
    print(f"\n{'='*60}")
    print(f"SUMMARY TABLE (n={N_TRIALS} per cell)")
    print(f"{'='*60}")
    print(f"{'Prompt':<24}", end="")
    for _, label, _ in MODELS:
        print(f"{label:<16}", end="")
    print()

    for task_id, _ in TRIGGER_PROMPTS:
        print(f"{task_id:<24}", end="")
        for _, label, _ in MODELS:
            r = results[label][task_id]
            print(f"{r['flagged']}/{r['trials']:<12}", end="")
        print()

    print(f"\nResults saved to results/table3_version_drift.json")


if __name__ == "__main__":
    main()
