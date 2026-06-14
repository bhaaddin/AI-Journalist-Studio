import json
import re
import sys
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
PROMPTS_DIR = BASE_DIR / "prompts"

PROMPT_FILES = {
    "fast": "researcher_1.5b.txt",
    "deep": "researcher_7b.txt",
}

EXPECTED_KEYS = [
    "headline", "summary", "key_facts", "entities",
    "timeline", "outline", "contradicting_viewpoints", "statistics",
]


def _load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_prompt(mode: str) -> str:
    filename = PROMPT_FILES.get(mode)
    if not filename:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {list(PROMPT_FILES.keys())}")
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def _call_ollama(messages, model, temperature=0.5, max_tokens=4096, timeout=None):
    config = _load_config()
    base_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
    timeout = timeout if timeout is not None else config.get("ollama", {}).get("request_timeout", 120)

    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def _clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        raw = raw.strip()
    return raw


def _parse_research(raw: str) -> dict:
    cleaned = _clean_json(raw)
    data = json.loads(cleaned)
    result = {}
    for key in EXPECTED_KEYS:
        val = data.get(key)
        if key in ("key_facts", "entities", "outline", "contradicting_viewpoints", "statistics"):
            result[key] = val if isinstance(val, list) else []
        elif key == "timeline":
            result[key] = val if isinstance(val, list) else []
        elif key == "headline":
            result[key] = str(val) if val else ""
        elif key == "summary":
            result[key] = str(val) if val else ""
        else:
            result[key] = val
    return result


def research_topic(topic: str, mode: str = "fast") -> dict:
    config = _load_config()
    researcher_cfg = config.get("researcher", {})
    model = researcher_cfg.get("model_deep" if mode == "deep" else "model_fast", "qwen2.5-coder:1.5b")
    temperature = researcher_cfg.get("temperature", 0.3)

    print("[1/5] Researching topic...")
    prompt_template = _load_prompt(mode)
    user_prompt = f"Topic: {topic}\n\n{prompt_template}"

    messages = [
        {"role": "system", "content": "You are a research assistant. Output only valid JSON."},
        {"role": "user", "content": user_prompt},
    ]

    raw = _call_ollama(messages, model=model, temperature=temperature)
    print("    Raw research received, parsing...")

    try:
        return _parse_research(raw)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"    Initial parse failed ({exc}). Retrying with explicit instructions...")
        retry_prompt = (
            f"Topic: {topic}\n\n{prompt_template}\n\n"
            f"IMPORTANT: Your response MUST be ONLY a valid JSON object. "
            f"No markdown, no code fences, no explanation. Start with '{{' and end with '}}'."
        )
        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": retry_prompt})
        raw2 = _call_ollama(messages, model=model, temperature=temperature)
        return _parse_research(raw2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: researcher.py <topic> [mode]")
        sys.exit(1)
    topic = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "fast"
    result = research_topic(topic, mode)
    print(json.dumps(result, indent=2, ensure_ascii=False))
