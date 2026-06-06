import os

os.environ.setdefault("PYTHONUTF8", "1")

def main() -> None:
	from ui.app import run
	run()

if __name__ == "__main__":
	main()
