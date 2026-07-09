"""Analyze PyInstaller Analysis toc and project asset sizes."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOC = ROOT / "build" / "MiraeseeApp" / "Analysis-00.toc"
ENTRY_RE = re.compile(
    r"\('([^']*)',\s*'([^']*)',\s*'(BINARY|DATA|EXTENSION)'\)"
)


def main() -> None:
    if not TOC.exists():
        print(f"Missing {TOC} — run pyinstaller first")
        return

    text = TOC.read_text(encoding="utf-8", errors="replace")
    by_prefix: dict[str, int] = defaultdict(int)
    sizes: list[tuple[int, str, str]] = []

    for dest, src, typ in ENTRY_RE.findall(text):
        p = Path(src)
        if not p.exists():
            continue
        sz = p.stat().st_size
        sizes.append((sz, dest, typ))
        top = dest.replace("\\", "/").split("/")[0]
        by_prefix[top] += sz

    sizes.sort(reverse=True)
    total = sum(s for s, _, _ in sizes)
    print(f"Analysis entries on disk: {len(sizes)}, total {total / 1e6:.1f} MB\n")
    print("By top-level prefix:")
    for k, v in sorted(by_prefix.items(), key=lambda x: -x[1]):
        print(f"  {v / 1e6:7.1f} MB  {k}")
    print("\nTop 30 files:")
    for sz, dest, typ in sizes[:30]:
        print(f"  {sz / 1e6:7.2f} MB  [{typ}]  {dest}")


if __name__ == "__main__":
    main()
