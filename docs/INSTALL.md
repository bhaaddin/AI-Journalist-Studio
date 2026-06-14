# Installation Guide

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/downloads)
- **Ollama** — [Download](https://ollama.com/download)
- **8GB+ RAM** (16GB recommended for deep mode)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/your_username/AI-Journalist-Studio.git
cd AI-Journalist-Studio
```

---

## Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

It is recommended to use a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

**Requirements installed:**
- `requests` — Ollama API communication
- `beautifulsoup4` — Web scraping (research phase)
- `markdown` — HTML export conversion
- `python-docx` — DOCX export
- `flask` — Web UI
- `pillow` — Image processing
- `duckduckgo_search` — Image collection
- `newspaper3k` — Article parsing

---

## Step 3: Pull Ollama Models

AI Journalist Studio uses two models by default:

```bash
# Fast research (1.5B parameters, ~1GB)
ollama pull qwen2.5-coder:1.5b

# Deep research model (7B parameters, ~4GB)
ollama pull qwen2.5-coder:7b

# Writer model (3B parameters, ~2GB)
ollama pull llama3.2:3b
```

> **Tip:** The deep research model is only needed for `--mode deep`. You can skip `qwen2.5-coder:7b` if you only use fast mode.

---

## Step 4: Start Ollama

```bash
ollama serve
```

Keep this terminal open. Ollama runs the API server at `http://localhost:11434`.

---

## Step 5: Run the Journalist

```bash
python journalist.py "Your article topic"
```

Or use the web UI:

```bash
python journalist.py --web
```

Then open `http://127.0.0.1:5000` in your browser.

---

## Windows-Specific Notes

### PDF Export

PDF export requires WeasyPrint, which needs **GTK3** on Windows.

1. Download GTK3 from the [WeasyPrint Windows docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)
2. Install and ensure `libweasyprint.dll` is in your PATH
3. Restart your terminal

If PDF export is not needed, skip this step — Markdown, HTML, and DOCX work without GTK.

### Long Paths

If you encounter path length errors, enable long path support:

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

---

## Troubleshooting

### "Connection refused" when running

Ensure Ollama is running:
```bash
ollama serve
```

Check the port in `config.json` — default is `http://localhost:11434`.

### "Model not found" errors

Pull the missing model:
```bash
ollama list           # shows installed models
ollama pull <model>   # downloads the model
```

### "Out of memory" / process killed

- Close other applications to free RAM
- Use `--mode fast` instead of deep (uses 1.5B model instead of 7B)
- Reduce `num_ctx` in `config.json` from 8192 to 4096
- Use a smaller writer model (`llama3.2:1b` or `qwen2.5-coder:1.5b`)

### "No module named 'xyz'"

Run the install again:
```bash
pip install -r requirements.txt
```

If using a virtual environment, make sure it's activated.

### JSON parsing errors during research

The researcher asks the LLM for strict JSON. If parsing fails repeatedly:

1. Use `--mode deep` — larger models produce cleaner JSON
2. Increase `num_ctx` in `config.json` to 16384
3. Check Ollama logs for model errors

### Web UI won't start

Port 5000 may be in use. Change the port in `config.json`:
```json
"web_ui": {
    "host": "127.0.0.1",
    "port": 5001,
    "debug": false
}
```

---

## Quick Install Scripts

| Platform | Script |
|----------|--------|
| Windows | `install.bat` |
| Linux / macOS | `bash install.sh` |
