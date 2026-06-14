import json
import sys
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
PROMPTS_DIR = BASE_DIR / "prompts"

WRITER_PROMPT = "writer_base.txt"
WRITER_HISTORIAN_PROMPT = "writer_historian.txt"


def _load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_prompt(filename: str) -> str:
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


def _build_article_prompt(research: dict, topic: str) -> str:
    sections = []
    sections.append(f"# Article Topic\n{topic}\n")
    sections.append(f"# Headline\n{research.get('headline', '')}\n")
    sections.append(f"# Summary\n{research.get('summary', '')}\n")

    key_facts = research.get("key_facts", [])
    if key_facts:
        sections.append("# Key Facts\n" + "\n".join(f"- {f}" for f in key_facts))

    entities = research.get("entities", [])
    if entities:
        sections.append("# Entities\n" + "\n".join(f"- {e}" for e in entities))

    timeline = research.get("timeline", [])
    if timeline:
        lines = []
        for entry in timeline:
            if isinstance(entry, dict):
                date = entry.get("date", "")
                event = entry.get("event", "")
                lines.append(f"- **{date}**: {event}")
            else:
                lines.append(f"- {entry}")
        sections.append("# Timeline\n" + "\n".join(lines))

    outline = research.get("outline", [])
    if outline:
        sections.append("# Suggested Outline\n" + "\n".join(f"- {s}" for s in outline))

    viewpoints = research.get("contradicting_viewpoints", [])
    if viewpoints:
        sections.append("# Contradicting Viewpoints\n" + "\n".join(f"- {v}" for v in viewpoints))

    statistics = research.get("statistics", [])
    if statistics:
        sections.append("# Statistics\n" + "\n".join(f"- {s}" for s in statistics))

    sections.append("\n# Article Structure (use this exact order)")
    sections.append("1. OPENING HOOK")
    sections.append("2. HISTORICAL ROOTS")
    sections.append("3. PRESENT SITUATION")
    sections.append("4. COMPARISON TABLE")
    sections.append("5. DEEP ANALYSIS")
    sections.append("6. FUTURE OUTLOOK")
    sections.append("7. KEY TAKEAWAYS")

    return "\n\n".join(sections)


def _is_refusal(text: str) -> bool:
    lower = text.lower()
    refusal_phrases = [
        "i cannot", "i can't", "i'm not able", "i am not able",
        "i apologize", "i'm sorry", "i cannot provide",
        "cannot fulfill", "cannot complete", "not appropriate",
        "as an ai", "as a language model", "i don't feel comfortable",
        "i will not", "won't write", "cannot write",
    ]
    return any(phrase in lower for phrase in refusal_phrases)


def write_article(research: dict, topic: str, mode: str = "fast") -> str:
    config = _load_config()
    writer_cfg = config.get("writer", {})
    model = writer_cfg.get(f"model_{mode}") or writer_cfg.get("model", "llama3.2:3b")
    temperature = writer_cfg.get("temperature", 0.5)
    max_tokens = writer_cfg.get("max_tokens", 4096)

    print("[2/5] Writing article...")
    prompt_template = _load_prompt(WRITER_PROMPT)
    research_block = _build_article_prompt(research, topic)
    user_prompt = f"{prompt_template}\n\n{research_block}"

    messages = [
        {"role": "system", "content": "You are a professional journalist writing a factual, well-structured article."},
        {"role": "user", "content": user_prompt},
    ]

    article = _call_ollama(messages, model=model, temperature=temperature, max_tokens=max_tokens)

    if _is_refusal(article):
        print("    Model refused. Retrying with historian persona...")
        return _write_with_historian(research, topic, model, temperature, max_tokens)

    if len(article.strip()) < 200:
        print(f"    Article too short ({len(article.strip())} chars). Retrying with more explicit prompt...")
        messages.append({"role": "assistant", "content": article})
        messages.append({
            "role": "user",
            "content": (
                "Write the full article now. Follow the 7-section structure exactly. "
                "Minimum 1500 words. Be thorough and specific."
            ),
        })
        article = _call_ollama(messages, model=model, temperature=temperature + 0.1, max_tokens=max_tokens)

        if _is_refusal(article):
            return _write_with_historian(research, topic, model, temperature, max_tokens)

    return article.strip()


def _write_with_historian(research: dict, topic: str, model: str, temperature: float, max_tokens: int) -> str:
    prompt_template = _load_prompt(WRITER_HISTORIAN_PROMPT)
    research_block = _build_article_prompt(research, topic)
    user_prompt = f"{prompt_template}\n\n{research_block}"

    messages = [
        {"role": "system", "content": "You are an independent historian in the year 2150 compiling the factual record."},
        {"role": "user", "content": user_prompt},
    ]

    article = _call_ollama(messages, model=model, temperature=temperature, max_tokens=max_tokens)
    return article.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: writer.py <topic> [research_json_file]")
        sys.exit(1)
    topic = sys.argv[1]
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as f:
            research = json.load(f)
    else:
        from researcher import research_topic
        research = research_topic(topic)
    article = write_article(research, topic)
    print(article)
