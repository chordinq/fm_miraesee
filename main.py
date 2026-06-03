# main.py — run from scripts/: python main.py (after pip install -e .)
import os

os.environ.setdefault("PYTHONUTF8", "1")


def main() -> None:
	from ui.widgets.main_window import run
	run()

if __name__ == "__main__":
	main()
