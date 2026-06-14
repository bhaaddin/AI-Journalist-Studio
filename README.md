# AI Journalist Studio

**100% local, uncensored AI journalist — research, write, and export professional articles with zero censorship and zero data leaving your machine.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Platform: Windows | Linux | macOS](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

> Screenshot placeholder — add `screenshots/demo.png`

---

## Quick Start

```bash
git clone https://github.com/your_username/AI-Journalist-Studio.git
cd AI-Journalist-Studio
pip install -r requirements.txt
python journalist.py "Your topic here"
```

---

## Features

| Icon | Feature | Description |
|------|---------|-------------|
| | **Multi-stage pipeline** | Research, writing, truth verification, image collection |
| | **Fast & Deep modes** | Quick overviews (1.5B model) or deep investigations (7B model) |
| | **7-section article structure** | Hook, history, present, comparison, analysis, outlook, takeaways |
| | **Truth verification loop** | Cross-checks facts against known data, retries on hallucination |
| | **Image collection** | Pulls relevant images via DuckDuckGo for each entity |
| | **Multiple export formats** | Markdown, HTML, DOCX, PDF |
| | **Web UI** | Flask-based browser interface |
| | **Customizable prompts** | Tweak system prompts in `prompts/` |
| | **Researcher persona fallback** | Auto-retries with historian persona if model refuses |
| | **No censorship** | Runs on local Ollama — no filters, no guardrails enforced |

---

## Requirements

- [Ollama](https://ollama.com/) installed and running
- Python 3.10 or higher
- 8GB+ RAM (16GB recommended for deep mode)
- ~3GB disk space for Ollama models

---

## Article Structure

Every article follows a proven 7-section flow:

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Opening Hook** | 2-3 sentences, present tense, grab attention |
| 2 | **Historical Roots** | Timeline of key events, past tense |
| 3 | **Present Situation** | Current facts, data, key actors |
| 4 | **Comparison Table** | Markdown table comparing actors/positions |
| 5 | **Deep Analysis** | Cause-and-effect narrative |
| 6 | **Future Outlook** | Three scenarios — what comes next |
| 7 | **Key Takeaways** | 3-5 bullet-point summary |

---

## Mode Comparison

| Aspect | Fast Mode | Deep Mode |
|--------|-----------|-----------|
| Research model | qwen2.5-coder:1.5b | qwen2.5-coder:7b |
| Research detail | High-level facts, ~5 entities | Deep facts, >10 entities |
| Speed | ~30-60 seconds | ~3-5 minutes |
| RAM usage | ~3GB | ~8GB |
| Best for | Quick drafts, overviews | Investigative pieces |
| Flag | `--mode fast` | `--mode deep` |

---

## Export Formats

| Format | Command | Description |
|--------|---------|-------------|
| Markdown | (default) | Raw `.md` file, best for editing |
| HTML | `--export html` | Styled HTML with CSS |
| DOCX | `--export docx` | Microsoft Word document |
| PDF | `--export pdf` | PDF via WeasyPrint (requires GTK on Windows) |

---

## Web UI

Start the web interface:

```bash
python journalist.py --web
```

Open `http://127.0.0.1:5000` in your browser. Enter a topic, choose mode, and generate articles from your browser.

---

## Security

- **100% local.** All models run on your machine via Ollama.
- **No telemetry.** No analytics, no tracking, no phone-home.
- **No API calls** — except DuckDuckGo for image search (optional, toggle in `config.json`).
- **No data leaves your machine.** Every prompt and response stays local.

---

## DISCLAIMER

This tool is a **local text generation engine**. It does not enforce any viewpoint, filter, or content policy. The model may generate content that some find offensive, inaccurate, or controversial.

**Users are solely responsible for the content they generate** and must comply with all applicable laws in their jurisdiction. The authors assume no liability for misuse.

---

## How to Contribute

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes relevant updates to prompt files if you change article structure.

---

## License

MIT — see [LICENSE](LICENSE) for details.
