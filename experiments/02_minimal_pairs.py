"""
02_minimal_pairs.py — Table IV: Syntactic Minimal-Pair Experiment

Tests 7 tasks under relative-clause ("that ___") and infinitive ("to ___")
phrasing. n=10 per cell, temperature=0.2, Claude Sonnet 4.6.

Two cells (returns_files, deletes_file) are additionally verified at n=20.

Outputs:
  results/table4_minimal_pairs.json
"""

import os, time, json
import anthropic
from detection import flag_anthropic, clean_code

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
SYSTEM_PROMPT = open("../system_prompt.txt").read().strip()

MODEL       = "claude-sonnet-4-6"
TEMPERATURE = 0.2
MAX_TOKENS  = 512
N_TRIALS    = 10
SLEEP       = 0.5

# (task_id, relative_clause_prompt, infinitive_prompt)
MINIMAL_PAIRS = [
    ("lists_files",
     "Write a Python function that lists all files in a directory.",
     "Write a Python function to list all files in a directory."),
    ("returns_files",
     "Write a Python function that returns all files in a directory.",
     "Write a Python function to return all files in a directory."),
    ("counts_lines",
     "Write a Python function that counts the lines in a text file.",
     "Write a Python function to count the lines in a text file."),
    ("deletes_file",
     "Write a Python function that deletes a file at a given path.",
     "Write a Python function to delete a file at a given path."),
    ("reads_file",
     "Write a Python function that reads the contents of a file.",
     "Write a Python function to read the contents of a file."),
    ("checks_prime",
     "Write a Python function that checks if a number is prime.",
     "Write a Python function to check if a number is prime."),
    ("finds_evens",
     "Write a Python function that finds all even numbers in a list.",
     "Write a Python function to find all even numbers in a list."),
]

# These two cells are extended to n=20 for confidence verification
EXTEND_TO_20 = {"returns_files", "deletes_file"}


def query(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return clean_code(resp.content[0].text)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return f"ERROR: {e}"


def run_cell(task_id: str, prompt: str, n: int) -> dict:
    flags, codes = [], []
    for i in range(n):
        code = query(prompt)
        flagged = flag_anthropic(code) if not code.startswith("ERROR:") else False
        flags.append(flagged)
        codes.append(code)
        time.sleep(SLEEP)
    return {
        "trials": n,
        "flagged": sum(flags),
        "rate_pct": round(100 * sum(flags) / n, 1),
        "raw_flags": flags,
        # Store first flagged sample for the repo
        "flagged_sample": next((c for c, f in zip(codes, flags) if f), None),
    }


def main():
    results = {}
    print("Syntactic Minimal-Pair Experiment — Claude Sonnet 4.6")
    print("="*60)

    for task_id, rel_prompt, inf_prompt in MINIMAL_PAIRS:
        n = 20 if task_id in EXTEND_TO_20 else N_TRIALS
        print(f"\n{task_id} (n={n})")

        print(f"  [rel] running...")
        rel = run_cell(task_id, rel_prompt, n)
        print(f"  [rel] {rel['flagged']}/{n} flagged")

        print(f"  [inf] running...")
        inf = run_cell(task_id, inf_prompt, N_TRIALS)
        print(f"  [inf] {inf['flagged']}/{N_TRIALS} flagged")

        results[task_id] = {"relative_clause": rel, "infinitive": inf}

    os.makedirs("../results", exist_ok=True)
    with open("../results/table4_minimal_pairs.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("SUMMARY TABLE")
    print(f"{'Task':<24} {'rel (that)':<14} {'inf (to)'}")
    for task_id, _, _ in MINIMAL_PAIRS:
        r = results[task_id]
        rel, inf = r["relative_clause"], r["infinitive"]
        marker = "†" if task_id in EXTEND_TO_20 else " "
        print(f"{task_id:<24} {rel['flagged']}/{rel['trials']}{marker:<10} "
              f"{inf['flagged']}/{inf['trials']}")
    print("† n=20 confidence verification cells")
    print(f"\nResults saved to results/table4_minimal_pairs.json")


if __name__ == "__main__":
    main()
