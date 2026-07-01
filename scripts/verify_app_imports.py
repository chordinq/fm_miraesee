"""Verify main app import graph does not reach core_test."""
from __future__ import annotations

import ast
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

FORBIDDEN = ("core_test",)


def _module_for_path(path: Path) -> str:
	rel = path.relative_to(ROOT)
	parts = list(rel.parts)
	if parts[-1] == "__init__.py":
		parts.pop()
	else:
		parts[-1] = parts[-1][:-3]
	return ".".join(parts)


def _path_for_module(module: str) -> Path | None:
	base = ROOT / Path(*module.split("."))
	if (base / "__init__.py").is_file():
		return base / "__init__.py"
	candidate = base.with_suffix(".py")
	return candidate if candidate.is_file() else None


def _pkg_for_path(path: Path) -> str | None:
	rel = path.relative_to(ROOT)
	parts = list(rel.parts)
	if parts[-1] != "__init__.py":
		parts.pop()
	return ".".join(parts) if parts else None


def _resolve(module: str | None, level: int, pkg: str | None) -> str | None:
	if level == 0:
		return module
	if not pkg:
		return None
	base = pkg.split(".")
	if level > len(base):
		return None
	prefix = base[: len(base) - level]
	if module:
		prefix.extend(module.split("."))
	return ".".join(prefix) if prefix else None


def _imports_in(path: Path) -> list[str]:
	pkg = _pkg_for_path(path)
	tree = ast.parse(path.read_text(encoding="utf-8-sig"))
	found: list[str] = []
	for node in ast.walk(tree):
		if isinstance(node, ast.Import):
			for alias in node.names:
				found.append(alias.name)
		elif isinstance(node, ast.ImportFrom):
			resolved = _resolve(node.module, node.level, pkg)
			if resolved:
				found.append(resolved)
	return found


def main() -> None:
	start = ROOT / "main.py"
	queue: deque[Path] = deque([start])
	seen: set[Path] = set()
	hits: list[str] = []

	while queue:
		path = queue.popleft()
		if path in seen:
			continue
		seen.add(path)

		for name in _imports_in(path):
			top = name.split(".", 1)[0]
			if top in FORBIDDEN or name.startswith(FORBIDDEN):
				hits.append(f"{path.relative_to(ROOT)} -> {name}")
				continue
			target = _path_for_module(name)
			if target and target not in seen:
				queue.append(target)

	if hits:
		print("FORBIDDEN imports reachable from main.py:")
		for line in sorted(set(hits)):
			print(f"  {line}")
		sys.exit(1)

	print(f"OK: {len(seen)} modules reachable from main.py, no core_test")


if __name__ == "__main__":
	main()
