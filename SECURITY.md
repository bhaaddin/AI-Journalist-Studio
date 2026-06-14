# Security Policy

## Current Status

AI Journalist Studio is a **local-only application**. There is no authentication, no user database, and no network service that accepts external connections by default.

- The Web UI binds to `127.0.0.1` (localhost only)
- All LLM inference runs locally via Ollama
- No user accounts, no sessions, no tokens

## Reporting a Vulnerability

If you discover a security issue, please **open a GitHub issue** with the label `security`. Do not email maintainers directly unless the issue is critical and requires a coordinated disclosure.

We aim to respond within 48 hours.

## Data Privacy

- **All processing is local.** Prompts, research data, and generated articles never leave your machine.
- **No telemetry.** This application does not collect usage statistics, crash reports, or analytics.
- **No external API calls** — except DuckDuckGo image search (optional, configurable in `config.json`).
- **Ollama runs locally.** Your conversations with the model stay on your hardware.

## Threat Model

| Threat | Mitigation |
|--------|------------|
| Remote code execution | Application has no network-exposed RPC endpoints |
| Data exfiltration | No outbound connections except DuckDuckGo (opt-in) |
| Model prompt injection | Runs on local Ollama — risk limited to local context |
| Unauthorized Web UI access | Binds to 127.0.0.1 only; not accessible from LAN/WAN |
| Dependency vulnerabilities | Use `pip install --upgrade` to keep dependencies current |

## Secure Configuration

- Keep `config.json` at default settings — sensitive fields are not present by design
- Run `ollama serve` in an isolated user session if multi-tenant environment
- Review `prompts/` files — they are system instructions passed verbatim to the model
- Disable DuckDuckGo image search in `config.json` if image collection is not needed:

```json
"image_collector": {
    "max_images_per_entity": 0
}
```

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x (current) | Yes |

We do not backport security fixes to older versions. Always use the latest release.
