<div align="center">
  <img src="photos/logo.png" alt="Alien's Eye Logo" width="400">
</div>

<h1 align="center">👁️ ALIEN'S EYE</h1>
<h3 align="center">AI-OSINT Username Reconnaissance Engine</h3>

<p align="center">
  <strong>840+ platforms · Async · ML-powered detection</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/aliens-eye"><img alt="PyPI" src="https://img.shields.io/pypi/v/aliens-eye?style=flat-square&logo=pypi"></a>
  <a href="https://github.com/DesusLove/Alian-s_Eye/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/DesusLove/Alian-s_Eye/ci.yml?style=flat-square&logo=github"></a>
  <a href="#"><img alt="Python" src="https://img.shields.io/pypi/pyversions/aliens-eye?style=flat-square&logo=python"></a>
  <a href="#"><img alt="License" src="https://img.shields.io/github/license/DesusLove/Alian-s_Eye?style=flat-square"></a>
</p>

---

## 📡 What is Alien's Eye?

A **terminal-based OSINT scanner** that checks 840+ social networks and web platforms for a given username in seconds. It doesn't just check HTTP status codes — it uses a **blend of ML and heuristic analysis** across 30 structural signals to distinguish real profiles from error pages, login walls, and landing pages.

---

## ✨ Capabilities

| Category | Features |
|----------|----------|
| **Detection** | ML + heuristic voting · 30-dim feature vectors · per-site fingerprints |
| **Scanning** | 840+ async sites · rate-limited · retry/backoff · Tor/proxy |
| **Extraction** | Display name, bio, avatar via OpenGraph, JSON-LD, and per-site CSS |
| **Recursion** | Extract usernames from bios and re-scan them (`--recurse-depth N`) |
| **Correlation** | Cluster profiles by avatar, bio, links (`--correlate`) · Domain checks (`--domains`) |
| **Watch** | Periodic re-scan with webhook alerts (`--watch 6h --notify <url>`) |
| **ML lifecycle** | Train custom models · hand-label uncertain results · self-check accuracy |
| **Outputs** | JSON, CSV, HTML, Markdown, PDF, XLSX, GEXF, Mermaid, Maltego |
| **Batch scan** | Scan from file (`--from-file usernames.txt`) |
| **History** | SQLite-backed scan history browsable via dashboard |
| **Web UI** | FastAPI dashboard (`alians_eye web`) |
| **Completions** | Shell autocompletion (`--completion bash\|zsh`) |
| **Extras** | Playwright fallback · Textual TUI · MCP server for LLM agents |

---

## 🚀 Quick Start

```bash
pip install aliens-eye

# One-shot scan
aliens_eye username

# Or with Docker
docker build -t aliens-eye .
docker run --rm -it aliens-eye username
```

### Optional Extras

```bash
pip install "aliens-eye[browser]"   # Playwright for JS-heavy pages
pip install "aliens-eye[train]"     # scikit-learn for retraining
pip install "aliens-eye[correlate]" # Pillow for avatar matching
pip install "aliens-eye[pdf]"       # PDF report generation
pip install "aliens-eye[tui]"       # Interactive terminal UI
pip install "aliens-eye[serve]"     # MCP server for LLM agents
pip install "aliens-eye[web]"       # Web dashboard (FastAPI)
pip install "aliens-eye[xlsx]"     # Excel export
```

From source:
```bash
git clone https://github.com/DesusLove/Alian-s_Eye.git
cd Aliens_eye
pip install -e .
```

---

## 🔍 Usage Examples

### Basic scanning
```bash
aliens_eye username
aliens_eye username1 username2
aliens_eye username -l advanced
aliens_eye username --site github,reddit
```

### Output & reporting
```bash
aliens_eye username --format all --output results
aliens_eye username --format pdf
aliens_eye username --only-found
```

### Advanced workflows
```bash
aliens_eye username --correlate --domains
aliens_eye username --recurse-depth 1
aliens_eye username --watch 6h --notify https://hooks.example/webhook
aliens_eye username --resume scan.jsonl
aliens_eye username --profile quick
```

### Batch scanning
```bash
aliens_eye --from-file usernames.txt
aliens_eye --from-file usernames.txt -l advanced
```

### Privacy & routing
```bash
aliens_eye username --tor
aliens_eye username --proxy socks5://127.0.0.1:1080
aliens_eye username --no-nsfw
```

### Utilities
```bash
aliens_eye diff results/old.json results/new.json
aliens_eye selfcheck --negatives 2
aliens_eye label results/report.json --out labeled.csv
aliens_eye tui username
aliens_eye serve
aliens_eye web --port 8765
aliens_eye --completion bash > /etc/bash_completion.d/alians_eye
```

---

## ⚙️ How Detection Works

Every HTTP response is transformed into a **30-dimensional feature vector**:

```
HTTP status  → 200, 3xx, 404, 4xx, 5xx buckets
URL analysis → username in path · canoncial url · redirect patterns
Keywords     → error keywords · positive keywords · meta analysis
DOM signals  → images · forms · profile/error CSS classes
Structure    → og:type=profile · JSON-LD Person schema
Timing       → response time · redirect count
Fingerprints → per-site learned patterns from past scans
```

Two judges score each vector:

| Judge | Method | Weight |
|-------|--------|--------|
| **Heuristic engine** | Weighted scoring over features | 60% |
| **ML model** | Logistic regression (trained on labeled data, runs in pure Python) | 40% |

The **blended probability** maps to one of three verdicts:

```
Found       (≥ threshold)     — high-confidence profile match
Maybe       (between thresholds) — uncertain, needs review
Not Found   (≤ threshold)     — no profile detected
```

If the ML model file is missing or corrupt, the scanner falls back to heuristics-only mode automatically.

---

## 🧠 Retraining the Model

```bash
pip install "aliens-eye[train]"

# 1. Collect labeled data
aliens_eye train collect --out dataset.csv --negatives 4

# 2. Train and export
aliens_eye train fit --data dataset.csv --out model.json

# 3. Use your custom model
aliens_eye username --model model.json
```

---

## 📁 Reports & Outputs

Scans are saved to the `results/` directory with timestamped filenames:

| Format | File | Content |
|--------|------|---------|
| JSON | `username_level_YYYYMMDD_HHMMSS.json` | Full per-site feature analysis |
| CSV | `username_level_YYYYMMDD_HHMMSS.csv` | Flat rows for spreadsheets |
| HTML | `username_level_YYYYMMDD_HHMMSS.html` | Standalone styled report |
| Markdown | `username_level_YYYYMMDD_HHMMSS.md` | Found/Maybe summary |
| PDF | `username_level_YYYYMMDD_HHMMSS.pdf` | Investigator report with avatars |
| GEXF / Mermaid / Maltego | Graph formats | Correlation visualization |

---

## 📐 Architecture

```
src/alians_eye/
├── core/           → scanner, detector, analyzer, http, exporter,
│                     fingerprints, config, correlate, domains,
│                     watch, checkpoints, variations, expand
├── ml/             → inference (pure Python), training, data collection,
│                     active labeling
├── utils/          → rich console output, logging, colors
├── data/           → sites.json (840+), model.json, nsfw filter,
│                     selfcheck ground-truth, site profiles
├── tui/            → Textual interactive browser
├── cli.py          → CLI entry point
├── mcp_server.py   → MCP protocol for LLM agent integration
└── selfcheck.py    → Accuracy validation
```

---

## 🔧 Configuration

Aliens Eye merges a JSON config file with CLI flags (CLI takes precedence). Config search path:

1. `./config.json` (current directory)
2. `~/.config/alians_eye/config.json` (platform config dir)
3. `%LOCALAPPDATA%\alians_eye\config.json` (Windows)

```json
{
  "concurrent": 50,
  "timeout": 10.0,
  "retries": 2,
  "rate_limit_delay": 0.2,
  "output_dir": "results",
  "output_formats": ["json", "csv", "html", "md"],
  "use_playwright": false,
  "proxy": null,
  "use_ml": true,
  "exclude_nsfw": false,
  "level": "basic"
}
```

Custom platform definitions can be dropped as `{ "name": "https://site/{}" }` JSON files into `./sites.d/` — they merge automatically.

---

## 🤝 Contributing

All contributions welcome:

- **Add sites** → edit `src/alians_eye/data/sites.json`
- **Improve detection** → expand `selfcheck.json` ground-truth
- **Retrain model** → collect better data, tune thresholds
- **Fix bugs** → PRs with passing tests appreciated

Before submitting:
```bash
ruff check src tests
pytest
```

---

## ⚠️ Disclaimer

> This tool is for **educational purposes and legitimate OSINT research** only. Users are responsible for complying with all applicable laws and platform terms of service. The authors assume no liability for misuse.
