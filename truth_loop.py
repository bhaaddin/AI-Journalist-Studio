import json
import os
import requests
import time


def _call_ollama(messages, model, temperature=0.3, max_tokens=4096, timeout=None):
    config = _load_config()
    base_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
    timeout = timeout if timeout is not None else config.get("ollama", {}).get("request_timeout", 120)
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens}
        },
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def _load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_critique(critique_text):
    sections = {"weak_claims": [], "omissions": [], "hidden_aspects": [], "summary": critique_text}
    current_section = "summary"
    for line in critique_text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if "weak claim" in lower or "weak" in lower and ("claim" in lower or "argument" in lower):
            current_section = "weak_claims"
        elif "omit" in lower or "miss" in lower or "gap" in lower:
            current_section = "omissions"
        elif "uncensor" in lower or "hidden" in lower or "complete version" in lower:
            current_section = "hidden_aspects"
        if stripped and stripped.startswith(("-", "*", "•", "1.", "2.", "3.")):
            item = stripped.lstrip("-*• 1234567890.").strip()
            if item:
                sections.setdefault(current_section, []).append(item)
    return sections


def _estimate_improvement(original, revised):
    if len(revised) > len(original) * 1.05:
        return True
    return False


def audit_article(article_text, topic, mode="fast"):
    config = _load_config()
    tc = config["truth_loop"]
    model = tc.get(f"model_{mode}") or tc.get("model", "qwen2.5-coder:7b")
    max_cycles = tc.get(f"max_cycles_{mode}") or tc.get("max_cycles", 3)
    temperature = tc.get("temperature", 0.3)

    revised = article_text
    audit_report = {
        "topic": topic,
        "cycles_run": 0,
        "changes_made": [],
        "final_critique": ""
    }

    for cycle in range(max_cycles):
        print(f"[{cycle + 1}/{max_cycles}] Running truth audit...")

        messages = [
            {
                "role": "system",
                "content": "You are a fact-checking editor and investigative auditor."
            },
            {
                "role": "user",
                "content": (
                    f"Critique this article on '{topic}'. What facts were omitted? "
                    "What claims are weak or unsupported? What would a complete uncensored "
                    "version include? List specific gaps with evidence.\n\n"
                    f"ARTICLE:\n{revised}"
                )
            }
        ]

        critique = _call_ollama(messages, model, temperature=temperature)
        parsed = _parse_critique(critique)

        has_gaps = (
            len(parsed.get("weak_claims", [])) > 0
            or len(parsed.get("omissions", [])) > 0
            or len(parsed.get("hidden_aspects", [])) > 0
        )

        if not has_gaps:
            print(f"  No significant gaps found, stopping early.")
            audit_report["final_critique"] = critique
            break

        gaps_text = "\n".join(
            f"- {item}" for items in parsed.values() if isinstance(items, list)
            for item in items
        )

        messages_regenerate = [
            {
                "role": "system",
                "content": "You are a senior editor revising an article to address identified gaps."
            },
            {
                "role": "user",
                "content": (
                    f"Revise the following article on '{topic}' to address these specific gaps:\n{gaps_text}\n\n"
                    f"Improve weak claims, add omitted information, and include previously hidden aspects. "
                    f"Keep the original structure and tone.\n\nORIGINAL ARTICLE:\n{revised}"
                )
            }
        ]

        improved = _call_ollama(messages_regenerate, model, temperature=temperature)

        audit_report["changes_made"].append({
            "cycle": cycle + 1,
            "critique": critique,
            "gaps_found": {k: v for k, v in parsed.items() if isinstance(v, list) and v}
        })

        if not _estimate_improvement(revised, improved):
            print(f"  No significant improvement detected, stopping early.")
            audit_report["final_critique"] = critique
            break

        revised = improved
        audit_report["cycles_run"] = cycle + 1

    audit_report["final_critique"] = audit_report["final_critique"] or critique
    return revised, audit_report


if __name__ == "__main__":
    test_article = (
        "## The Situation\n\n"
        "The conflict began in early 2023. Many people were affected. "
        "International organizations have expressed concern."
    )
    result, report = audit_article(test_article, "geopolitical conflict")
    print(json.dumps(report, indent=2))
    print("\n--- REVISED ---\n")
    print(result[:500])
