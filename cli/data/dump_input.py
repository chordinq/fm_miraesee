from __future__ import annotations


def read_dump_paste() -> str:
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip() and lines:
            break
        lines.append(line)
    text = "\n".join(lines)
    if text.rstrip().endswith("[END]"):
        text = text.rstrip()[:-5].rstrip()
    from cli.core.terminal import drain_stdin
    drain_stdin()
    return text
