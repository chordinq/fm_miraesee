# cli/ui/app.py — main application loop
from __future__ import annotations

from cli.core.terminal import ui_session
from cli.core.presenter import show_frame
from cli.theme import dim


def run(session) -> None:
    from cli.ui.screens import main_menu, run_hub, options, about

    with ui_session():
        while True:
            choice = main_menu.run()
            if choice == "run":
                run_hub.run(session)
            elif choice == "options":
                options.run()
            elif choice == "about":
                about.run()
            elif choice == "exit":
                show_frame([dim("  Goodbye.")])
                return
