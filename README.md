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
python sprite_preview.py
python -m ui.tests.sprite_preview
```

Run commands from `scripts/` (project root). Do not run `ui/app.py` directly as a file — use the commands above.

## Layout

- `config/` — paths (`paths.py`) and JSON loaders
- `core/` — enums, player model, simulators
- `ui/` — Qt sprites and previews
- `assets/` — game JSON and sprites
