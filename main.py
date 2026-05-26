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
    if sys.platform == "win32":
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)

    from cli.core.terminal import set_theme, drain_stdin
    from cli.data.dump_input import read_dump_paste
    from cli.data.dump_welcome import show_dump_screen
    from cli.services.build_session import rebuild_session
    from cli.ui.app import run
    from cli.theme import dim

    set_theme()
    show_dump_screen()
    dump = read_dump_paste()
    drain_stdin()

    if not dump.strip():
        print(dim("\n  No dump. Exiting.\n"))
        return

    session = rebuild_session(dump)
    if session is None:
        return

    run(session)


if __name__ == "__main__":
    main()
