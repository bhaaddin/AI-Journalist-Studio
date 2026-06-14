# Usage Guide

## CLI Commands

### Generate an article

```bash
python journalist.py "The geopolitics of rare earth minerals"
```

### Fast mode (default)

```bash
python journalist.py --mode fast "Climate change in Southeast Asia"
```

### Deep mode (detailed investigation)

```bash
python journalist.py --mode deep "The history of quantum computing"
```

### Export to specific format

```bash
python journalist.py --export html "AI regulation in the EU"
python journalist.py --export docx "Mars colonization plans"
python journalist.py --export pdf "The economics of space mining"
```

### Combine flags

```bash
python journalist.py --mode deep --export docx "Nuclear fusion breakthroughs"
```

### Start the web UI

```bash
python journalist.py --web
```

---

## Mode Switching

| Flag | Model | Detail Level | Speed |
|------|-------|-------------|-------|
| `--mode fast` | qwen2.5-coder:1.5b | Surface-level research | ~30-60s |
| `--mode deep` | qwen2.5-coder:7b | Deep-dive investigation | ~3-5 min |

Fast mode is best for:
- Daily news summaries
- Quick drafts
- Topics you already know well

Deep mode is best for:
- Investigative pieces
- Historical analysis
- Topics requiring specific facts and dates

---

## Article Types

The pipeline supports different article styles via prompt files in `prompts/`:

| Prompt File | Style |
|-------------|-------|
| `writer_base.txt` | Standard journalistic article (default) |
| `writer_historian.txt` | Historical/analytical perspective (fallback) |

Add new prompt files to `prompts/` and reference them in your workflow. See [Adding New Prompt Files](#adding-new-prompt-files).

---

## Web UI

Start the web interface:

```bash
python journalist.py --web
```

Navigate to `http://127.0.0.1:5000`.

### UI features:
- **Topic input** — Enter any article topic
- **Mode selector** — Toggle Fast / Deep
- **Export dropdown** — Choose output format
- **Generate button** — Run the full pipeline
- **Article preview** — Read the result in-browser
- **Download links** — Save generated files

---

## Export Formats

| Format | Option | Dependencies | Description |
|--------|--------|-------------|-------------|
| Markdown | `--export md` | None | Raw `.md` file, editable in any text editor |
| HTML | `--export html` | `markdown` | Styled HTML page with article structure |
| DOCX | `--export docx` | `python-docx` | Microsoft Word `.docx` with basic formatting |
| PDF | `--export pdf` | WeasyPrint + GTK | Print-ready PDF with typography |

Files are saved to the `exports/` directory with a timestamped filename.

---

## Custom Configuration

Edit `config.json` to tune the pipeline:

```json
{
  "researcher": {
    "model_fast": "qwen2.5-coder:1.5b",
    "model_deep": "qwen2.5-coder:7b",
    "num_ctx": 8192,
    "temperature": 0.3
  },
  "writer": {
    "model": "llama3.2:3b",
    "num_ctx": 8192,
    "temperature": 0.5,
    "max_tokens": 4096
  },
  "truth_loop": {
    "model": "qwen2.5-coder:7b",
    "max_cycles": 3,
    "temperature": 0.3
  },
  "image_collector": {
    "max_images_per_entity": 3,
    "delay_between_searches": 2.0,
    "safe_search": "off"
  },
  "ollama": {
    "base_url": "http://localhost:11434",
    "request_timeout": 120
  },
  "web_ui": {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": false
  }
}
```

### Key settings:

| Setting | Default | Notes |
|---------|---------|-------|
| `researcher.temperature` | 0.3 | Lower = more factual, higher = more creative |
| `writer.temperature` | 0.5 | Bump to 0.7 for more narrative flair |
| `writer.max_tokens` | 4096 | Increase for longer articles (max depends on model) |
| `truth_loop.max_cycles` | 3 | Higher = more thorough but slower |
| `ollama.request_timeout` | 120 | Increase if your model is slow |
| `web_ui.port` | 5000 | Change if port is in use |

---

## Adding New Prompt Files

1. Create a new `.txt` file in `prompts/`
2. Write your system prompt — the researcher prompt expects JSON output, the writer prompt expects article text
3. Reference it in your workflow or modify the code to load it

Example custom writer prompt (`prompts/writer_editorial.txt`):

```text
You are an opinion columnist. Write a persuasive editorial...
```

To use it, modify `writer.py`:

```python
WRITER_PROMPT = "writer_editorial.txt"
```

---

## Pipeline Stages

| # | Stage | Script | Function | Description |
|---|-------|--------|----------|-------------|
| 1 | Research | `researcher.py` | `research_topic()` | Generates structured research JSON (facts, entities, timeline) |
| 2 | Writing | `writer.py` | `write_article()` | Composes article from research using 7-section structure |
| 3 | Truth Loop | `truth_loop.py` | `verify_article()` | Cross-checks facts, retries if hallucination detected |
| 4 | Image Collection | `image_collector.py` | `collect_images()` | Fetches images for named entities via DuckDuckGo |
| 5 | Export | `writer.py` | — | Converts article to Markdown, HTML, DOCX, or PDF |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL (overrides `config.json`) |

---

## Examples

### Quick news article

```bash
python journalist.py "What happened at COP29"
```

### Deep investigation with DOCX export

```bash
python journalist.py --mode deep --export docx "The fall of the Roman Empire"
```

### HTML export for web publishing

```bash
python journalist.py --export html "Renaissance art and modern science"
```

### Serve as a local web app

```bash
python journalist.py --web
```
