"""Format rows into instruction-tuning text."""
from __future__ import annotations

PROMPT_TEMPLATE = """### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""


def format_alpaca(example: dict) -> dict:
    return {
        "text": PROMPT_TEMPLATE.format(
            instruction=(example.get("instruction") or "").strip(),
            input=(example.get("input") or "").strip(),
            output=(example.get("output") or "").strip(),
        )
    }


def format_chatml(example: dict, tokenizer) -> dict:
    """ChatML format used by newer models."""
    messages = [
        {"role": "system", "content": "You are a helpful, safe assistant."},
        {"role": "user", "content": f"{example.get('instruction','')}\n{example.get('input','')}".strip()},
        {"role": "assistant", "content": example.get("output", "")},
    ]
    return {"text": tokenizer.apply_chat_template(messages, tokenize=False)}
