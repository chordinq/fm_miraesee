# main.py
import os
import sys
import io

_ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PYTHONUTF8", "1")
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except AttributeError:
        pass
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main() -> None:
    from ui.app import run

    run()


if __name__ == "__main__":
    main()
