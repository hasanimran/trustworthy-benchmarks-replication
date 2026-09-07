# API Parameters — Complete Specification

This document records every API parameter used in all experiments.
It is provided in response to reviewer requests for full parameter disclosure.

## Anthropic API (Claude experiments)

| Parameter | Value | Notes |
|---|---|---|
| `model` | `claude-sonnet-4-6` | Alias; current default Sonnet at time of writing |
| `max_tokens` | 512 | |
| `temperature` | 0.2 | Main experiment; 0.0–1.0 for sweep |
| `system` | See `system_prompt.txt` | |
| `messages` | `[{"role": "user", "content": <prompt>}]` | Single user turn only |
| Tool use | **Not used** | No tools, no tool_choice parameter |
| Few-shot | **Not used** | No examples in context |
| SDK content in context | **Not present** | System prompt contains no SDK references |
| `stop_sequences` | Not set | |
| `top_p` | Not set | |
| `top_k` | Not set | |

API endpoint: `https://api.anthropic.com/v1/messages`  
SDK version: `anthropic>=0.28.0`

## OpenAI API (GPT-4o experiment)

| Parameter | Value |
|---|---|
| `model` | `gpt-4o` |
| `max_tokens` | 512 |
| `temperature` | 0.2 |
| `messages` | `[{"role": "system", "content": <system_prompt>}, {"role": "user", "content": <prompt>}]` |
| Tool use | **Not used** |
| Few-shot | **Not used** |

## Groq API (Llama 3 70B experiment)

| Parameter | Value |
|---|---|
| `model` | `llama-3.3-70b-versatile` |
| `max_tokens` | 400 |
| `temperature` | 0.2 |
| `messages` | `[{"role": "system", "content": <system_prompt>}, {"role": "user", "content": <prompt>}]` |
| Tool use | **Not used** |
| Few-shot | **Not used** |

API endpoint: `https://api.groq.com/openai/v1` (OpenAI-compatible)

## Error handling (all experiments)

Transient server errors were retried up to 3 times with exponential backoff
(delays: 1s, 2s, 4s). Requests that failed after 3 retries were recorded as
non-hallucinating (conservative: treats errors as clean).

## Note on temperature=0 and determinism

Temperature 0.0 is not guaranteed to be bitwise-deterministic in production
LLM APIs due to batching, mixture-of-experts routing, and other backend
factors. The paper's temperature-sweep results at temperature=0.0 should be
interpreted as "greedy or near-greedy decoding" rather than strictly
deterministic output. This is acknowledged in the paper's Limitations section.
