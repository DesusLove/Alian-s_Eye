# Changelog

## 2.2.2 (2026-07-17)

### Changed
- Forked and rebranded to **Alien's Eye**
- Module renamed from `aliens_eye` to `alians_eye`
- PyPI package: `aliens-eye` (apostrophe invalid in package names; display name uses `Alien's Eye`)
- All imports, resource paths, and config directories updated
- README completely rewritten with new structure and logo
- New SVG logo and screenshot-based logo asset

## 2.0.0 (2026-06-11)

### Added
- **PyPI package**: `pip install aliens-eye` with `alians_eye` console command
- **Real ML detection**: logistic-regression model trained on labeled scans, blended with the heuristic engine; pure-python inference with zero ML runtime dependencies
- `alians_eye train collect` / `alians_eye train fit` for building datasets and retraining the model
- `alians_eye selfcheck`: validates detection accuracy against accounts known to exist
- **Rich terminal UI**: live progress bar, sorted result tables, summary panels; `--plain` for scripts
- **Proxy support**: `--proxy` (HTTP/SOCKS4/SOCKS5) and `--tor`
- **Site filtering**: `--site`, `--exclude-site`, `--no-nsfw`
- Markdown report export (`--format md`)
- `--profile quick|full|aggressive` for non-interactive preset selection
- `--version`, `--sites` (custom site list), `--model` (custom model), `--no-ml`
- Dockerfile
- Test suite (pytest) and GitHub Actions CI (lint + tests on Linux/Windows, Python 3.10–3.13)
- Automated PyPI release workflow via trusted publishing

### Changed
- Restructured to a `src/alians_eye/` package; `sites.json` and the model ship as package data
- Playwright is now an optional extra: `pip install aliens-eye[browser]`
- Fingerprint cache and config moved to platform-standard directories (via `platformdirs`)
- Confidence is now derived from a calibrated probability instead of fixed score bands

### Removed
- Hardcoded `/etc`, `/usr/local`, and Termux path probing
- Dead `mumble://` site entry

### Compatibility
- `python alians_eye.py` from a source checkout still works
