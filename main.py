import os
import sys

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR", "1")


def main() -> None:
	from app.run import main as run_app

	run_app()


if __name__ == "__main__":
	main()
