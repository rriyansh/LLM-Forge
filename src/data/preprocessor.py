"""Convert Alpaca-style rows into a single training text prompt."""
from __future__ import annotations

PROMPT_TEMPLATE = """### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""


def format_example(example: dict) -> dict:
    instruction = (example.get("instruction") or "").strip()
    inp = (example.get("input") or "").strip()
    output = (example.get("output") or "").strip()
    text = PROMPT_TEMPLATE.format(instruction=instruction, input=inp, output=output)
    return {"text": text}
