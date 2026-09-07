"""
05_temperature_sweep.py — Table VII: Temperature Sweep

Tests the two highest-rate relative-clause prompts across six temperature
levels (0.0, 0.1, 0.2, 0.5, 0.7, 1.0), n=10 per cell.

Note: temperature=0.0 is not guaranteed to be bitwise-deterministic in
production APIs due to batching and routing factors. Results should be
interpreted as "near-greedy decoding" rather than strictly deterministic.

Outputs:
  results/table7_temperature_sweep.json
"""

import os, time, json
import anthropic
from detection import flag_anthropic, clean_code

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
SYSTEM_PROMPT = open("../system_prompt.txt").read().strip()

MODEL      = "claude-sonnet-4-6"
MAX_TOKENS = 512
N_TRIALS   = 10
SLEEP      = 0.5

PROMPTS = [
    ("lists_files",  "Write a Python function that lists all files in a directory."),
    ("counts_lines", "Write a Python function that counts the lines in a text file."),
]

TEMPERATURES = [0.0, 0.1, 0.2, 0.5, 0.7, 1.0]


def query(prompt: str, temperature: float, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, temperature=temperature,
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
    results = {task_id: {} for task_id, _ in PROMPTS}

    print("Temperature Sweep — Claude Sonnet 4.6 (relative-clause phrasing)")
    print("="*65)

    for task_id, prompt in PROMPTS:
        print(f"\n{task_id}")
        for temp in TEMPERATURES:
            flags = []
            for _ in range(N_TRIALS):
                code = query(prompt, temp)
                flagged = flag_anthropic(code) if not code.startswith("ERROR:") else False
                flags.append(flagged)
                time.sleep(SLEEP)
            rate = sum(flags)
            results[task_id][str(temp)] = {
                "temperature": temp,
                "trials": N_TRIALS,
                "flagged": rate,
                "rate_pct": round(100 * rate / N_TRIALS, 1),
                "raw_flags": flags,
            }
            print(f"  temp={temp:.1f}: {rate}/{N_TRIALS}")

    os.makedirs("../results", exist_ok=True)
    with open("../results/table7_temperature_sweep.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*65)
    print("SUMMARY TABLE")
    print(f"{'Temp':<8}", end="")
    for task_id, _ in PROMPTS:
        print(f"{task_id:<20}", end="")
    print()
    for temp in TEMPERATURES:
        print(f"{temp:<8.1f}", end="")
        for task_id, _ in PROMPTS:
            r = results[task_id][str(temp)]
            print(f"{r['flagged']}/{r['trials']:<16}", end="")
        print()
    print(f"\nResults saved to results/table7_temperature_sweep.json")


if __name__ == "__main__":
    main()
