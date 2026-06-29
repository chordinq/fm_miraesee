import os

os.environ.setdefault("PYTHONUTF8", "1")


def main() -> None:
    from app.run import main as run_app

    run_app()


if __name__ == "__main__":
    main()
