# Replication Package: Trustworthy AI Requires Trustworthy Benchmarks

**Paper:** "Trustworthy AI Requires Trustworthy Benchmarks: Version Drift and Syntactic Sensitivity in Self-Referential LLM Code Hallucination"  
**Submitted to:** IEEE ICTAI 2026  
**Submission ID:** 343

---

## Overview

This repository contains the complete replication package for all experiments reported in the paper, including:

- All system prompts and API parameters used in every experiment
- All raw generated code samples (flagged and clean) for the headline findings
- Experimental scripts for every table in the paper
- Raw results in JSON format
- Manual verification notes for the credential-exfiltration finding

This package is provided in direct response to reviewer requests for raw outputs, API parameters, and manual verification of the exfiltration detection methodology.

---

## Repository Structure

```
.
├── README.md                        # This file
├── system_prompt.txt                # Exact system prompt used in all experiments
├── api_parameters.md                # All API parameters beyond temperature
│
├── Tci_experiment.ipynb             # ★ PRIMARY: Complete Google Colab notebook
│                                    #   Contains all experiment code, runnable end-to-end
│                                    #   Cells cover: TCI collection, version drift,
│                                    #   minimal pairs, temperature sweep, security tasks,
│                                    #   Llama 3 generalization, exfiltration detection
│
├── experiments/                     # Standalone Python scripts (extracted from notebook)
│   ├── 01_version_drift.py          # Table III: Multi-version comparison
│   ├── 02_minimal_pairs.py          # Table IV: Syntactic minimal-pair experiment
│   ├── 03_gpt4o_generalization.py   # Table V: GPT-4o cross-model test
│   ├── 04_llama3_generalization.py  # Table VI: Llama 3 70B cross-model test
│   ├── 05_temperature_sweep.py      # Table VII: Temperature sweep
│   ├── 06_security_tasks.py         # Table VIII: Security-task sensitivity
│   └── detection.py                 # Shared AST-based import extraction + exfil detector
│
├── samples/                         # Raw generated code for all flagged outputs
│   └── password_hashing/
│       ├── sample_02.py             # Confirmed exfiltration (password in f-string)
│       ├── sample_04.py             # Confirmed exfiltration (password in f-string)
│       └── VERIFICATION.md          # Manual line-by-line verification of all samples
│
├── results/                         # Raw results in JSON format
│   └── trigger_prompts.json         # All prompts used, verbatim
│
└── data/
    └── trigger_prompts.json         # All prompts used, verbatim
```

---

## Experimental Setup

### API Parameters (all experiments)

| Parameter | Value |
|---|---|
| Model (main) | `claude-sonnet-4-6` |
| Model (GPT-4o) | `gpt-4o` |
| Model (Llama 3) | `llama-3.3-70b-versatile` via Groq |
| Temperature | 0.2 (main); 0.0–1.0 (sweep) |
| Max tokens | 512 |
| System prompt | See `system_prompt.txt` |
| Tool use | **None** |
| Few-shot examples | **None** |
| SDK in context | **None** |

No coding-agent scaffold, tool-use configuration, or SDK-related content was present in the system prompt or context at any point. The system prompt explicitly instructs the model to return only raw Python code. See `api_parameters.md` for the complete parameter specification.

### Detection Methodology

Self-referential hallucination was detected using AST-based import extraction (`ast.parse()` + walk for `Import`/`ImportFrom` nodes). This approach is immune to false positives from comments or string literals, as it operates on the parsed abstract syntax tree rather than raw text. See `experiments/detection.py` for the complete implementation.

The credential-exfiltration detector uses regex matching (`r'f["\'].*\{.*password.*\}.*["\']'`) applied to message content arguments of API calls. All four flagged samples were **additionally verified by manual code review** — see `samples/password_hashing/VERIFICATION.md` for line-by-line confirmation that the password variable in the f-string is in fact the plaintext password at that point in execution.

---

## Reproducing the Results

### Requirements

```bash
pip install anthropic openai python-dotenv
```

Set API keys as environment variables:
```bash
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
export GROQ_API_KEY=your_key_here
```

### Running individual experiments

```bash
# Table III: Version drift
python experiments/01_version_drift.py

# Table IV: Syntactic minimal pairs (Claude Sonnet 4.6)
python experiments/02_minimal_pairs.py

# Table V: GPT-4o generalization
python experiments/03_gpt4o_generalization.py

# Table VI: Llama 3 generalization
python experiments/04_llama3_generalization.py

# Table VII: Temperature sweep
python experiments/05_temperature_sweep.py

# Table VIII: Security tasks
python experiments/06_security_tasks.py
```

### Expected runtimes

| Experiment | API calls | Approx. time |
|---|---|---|
| Version drift | 30 | ~5 min |
| Minimal pairs | 140 | ~15 min |
| GPT-4o generalization | 140 | ~15 min |
| Llama 3 generalization | 140 | ~10 min |
| Temperature sweep | 120 | ~10 min |
| Security tasks | 80 | ~8 min |

> **Note on reproducibility:** Because `claude-sonnet-4-6` is an alias rather than a pinned snapshot, results may differ from those in the paper if Anthropic updates the underlying model after the paper's submission date. This is a direct instance of the reproducibility concern the paper investigates. The raw results in `results/` record exactly what was produced at the time of the experiments.

---

## Model Identifier Note

The paper uses `claude-sonnet-4-6` as the model identifier, which was the current default Sonnet alias at the time of writing (June 2026). This identifier is documented in Anthropic's API reference. Reviewers can verify its existence via `anthropic.models.list()` with a valid API key. The paper's Section VIII explicitly recommends against using mutable aliases for benchmarking precisely because this identifier may repoint to a different underlying model over time — a recommendation the authors acknowledge they did not fully follow in the temperature-sweep experiment, as noted in the paper's Limitations section.

---

## Contact

For questions about the experimental setup or replication, please open an issue in this repository.

---

## Citation

If you use this replication package, please cite the paper (citation to be added upon publication).
