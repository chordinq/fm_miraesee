# Miraesee scripts

Python tooling for game logic, simulators, and UI previews.

## Setup (once)

From this directory (`scripts/`):

```bash
pip install -e .
```

This registers `config`, `core`, `ui`, and `utils` on your Python path. No `sys.path` hacks required.

## Run

```bash
python main.py
python ui/test/test.py
python ui/test/test_game.py
python sprite_preview.py
```

Run commands from `scripts/` (project root).

## Layout

- `config/` — paths (`paths.py`) and JSON loaders
- `core/` — enums, player model, simulators
- `controllers/` — Python ↔ QML bridges (`Property`, `Signal`, `Slot`)
- `app/` — QML bootstrap, session orchestration
- `ui/` — QML widgets, component preview harnesses (`ui/test/`)
- `utils/` — dump ingest, shared non-UI helpers
- `assets/` — game JSON and sprites
