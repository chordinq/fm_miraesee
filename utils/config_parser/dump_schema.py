"""Parse GameConfigEntry and MetaMember schemas from Il2Cpp dump.cs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_DUMP = Path(__file__).resolve().parents[2] / "dump.cs"

_META_MEMBER = re.compile(
    r"\[MetaMember\((\d+),[^\]]*\)\]"
    r"(?:\s*\[[^\]]+\])*"
    r"\s*public ([\w.?<>,\[\]]+) (\w+)"
)


@dataclass
class MemberSchema:
    tag: int
    type_name: str
    name: str


@dataclass
class ClassSchema:
    name: str
    members: dict[int, MemberSchema] = field(default_factory=dict)
    base: str | None = None
    key_type: str | None = None
    is_enum: bool = False
    enum_values: dict[int, str] = field(default_factory=dict)


@dataclass
class EntrySchema:
    file_name: str
    kind: str  # "keyvalue" | "table"
    class_name: str
    key_type: str | None = None


def _parse_enums(text: str) -> dict[str, ClassSchema]:
    enums: dict[str, ClassSchema] = {}
    current: str | None = None
    for line in text.splitlines():
        m = re.match(r"(?:\[[^\]]+\]\s*)*public enum (\w+)", line)
        if m:
            current = m.group(1)
            enums[current] = ClassSchema(name=current, is_enum=True)
            continue
        if current:
            cm = re.match(r"\s*public const \w+ (\w+) = (-?\d+);", line)
            if cm:
                enums[current].enum_values[int(cm.group(2))] = cm.group(1)
            elif line.strip() == "}":
                current = None
    return enums


_CLASS_DECL = re.compile(
    r"public (?:(?:abstract|sealed) )?(?:class|struct) (\w+)(?: : ([\w, ]+))?"
)
_NESTED_DECL = re.compile(
    r"public (?:(?:abstract|sealed) )?(?:class|struct|enum|interface) "
)


def _parse_classes(text: str) -> dict[str, ClassSchema]:
    classes: dict[str, ClassSchema] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _CLASS_DECL.match(line)
        if not m:
            i += 1
            continue
        name = m.group(1)
        bases = m.group(2) or ""
        base = bases.split(",")[0].strip() if bases else None
        body: list[str] = []
        i += 1
        while i < len(lines):
            ln = lines[i]
            if _NESTED_DECL.match(ln) and not ln.strip().startswith("//"):
                break
            if ln.strip() == "}" and body:
                break
            body.append(ln)
            i += 1
        block = "\n".join(body)
        if "[MetaMember(" not in block and name not in ("ItemId", "BattleId", "PetId", "MountId", "SkinId"):
            if base and name not in classes:
                classes[name] = ClassSchema(name=name, base=base or None)
            continue
        schema = ClassSchema(name=name, base=base or None)
        km = re.search(r"IGameConfigData<(\w+)>", line + bases)
        if km:
            schema.key_type = km.group(1)
        km = re.search(r"IHasGameConfigKey<(\w+)>", line + bases)
        if km:
            schema.key_type = km.group(1)
        for mm in _META_MEMBER.finditer(block):
            tag = int(mm.group(1))
            schema.members[tag] = MemberSchema(tag, mm.group(2).strip(), mm.group(3))
        classes[name] = schema
    return classes


def _parse_entries(text: str) -> dict[str, EntrySchema]:
    entries: dict[str, EntrySchema] = {}
    pattern = re.compile(
        r'\[GameConfigEntry\("([^"]+)"[^\]]*\)\]\s*'
        r"(?:\[[^\]]+\]\s*)*"
        r"public (?:GameConfigLibrary<([^,]+),\s*([^>]+)>|(\w+))",
    )
    for m in pattern.finditer(text):
        file_name = m.group(1)
        if m.group(2):
            entries[file_name] = EntrySchema(
                file_name=file_name,
                kind="table",
                class_name=m.group(3).strip(),
                key_type=m.group(2).strip(),
            )
        else:
            entries[file_name] = EntrySchema(
                file_name=file_name,
                kind="keyvalue",
                class_name=m.group(4).strip(),
            )
    return entries


class SchemaRegistry:
    def __init__(self, dump_path: Path | None = None) -> None:
        path = (dump_path or DEFAULT_DUMP).resolve()
        self.dump_path = path
        text = path.read_text(encoding="utf-8", errors="ignore")
        self.enums = _parse_enums(text)
        self.classes = _parse_classes(text)
        self.entries = _parse_entries(text)

    def get_class(self, name: str) -> ClassSchema | None:
        base = name.rstrip("?")
        if base in self.enums:
            return self.enums[base]
        cls = self.classes.get(base)
        if cls is None:
            return None

        members: dict[int, MemberSchema] = {}
        key_type = cls.key_type
        chain: list[ClassSchema] = []
        cur: ClassSchema | None = cls
        seen: set[str] = set()
        while cur and cur.name not in seen:
            seen.add(cur.name)
            chain.append(cur)
            if cur.key_type:
                key_type = cur.key_type
            cur = self.classes.get(cur.base) if cur.base else None

        for part in reversed(chain):
            members.update(part.members)

        if not members and not key_type:
            return cls

        return ClassSchema(name=cls.name, base=cls.base, key_type=key_type, members=members)

    def enum_name(self, type_name: str, value: int) -> str | int:
        base = type_name.rstrip("?")
        enum = self.enums.get(base)
        if enum and value in enum.enum_values:
            return enum.enum_values[value]
        return value


_registry: SchemaRegistry | None = None


def get_registry(dump_path: Path | None = None) -> SchemaRegistry:
    global _registry
    path = (dump_path or DEFAULT_DUMP).resolve()
    if _registry is None or _registry.dump_path != path:
        _registry = SchemaRegistry(path)
    return _registry
