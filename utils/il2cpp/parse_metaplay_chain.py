#!/usr/bin/env python3
"""Parse Il2CppDumper output + global-metadata.dat for Metaplay PlayerModel chain calibration."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

METADATA_MAGIC = 0xFAB11BAF
IL2CPP_OBJECT_HEADER = 0x10
POINTER_SIZE = 8
ALIGNMENT = 8

IL2CPP_RUNTIME_LAYOUT = {
    "Il2CppClass_1_size": 0xB8,
    "Il2CppClass": {
        "static_fields": 0xB8,
        "rgctx_data": 0xC0,
    },
    "MethodInfo": {
        "methodPointer": 0x0,
        "virtualMethodPointer": 0x8,
        "invoker_method": 0x10,
        "name": 0x18,
        "klass": 0x20,
        "return_type": 0x28,
        "parameters": 0x30,
        "rgctx_data": 0x38,
        "genericMethod": 0x40,
        "token": 0x48,
    },
}

STRUCT_LAYOUT_OVERRIDES: dict[str, dict[str, int]] = {
    "Metaplay_Core_Model_Timeline_TModel__ModelJournal_Leader_StagedOp_TModel___ModelJournal_Leader_StagedStep_TModel___Fields": {
        "_stagedModel": 0x50,
    },
    "Metaplay_Core_Model_JournalPosition_Fields": {
        "Tick": 0x0,
        "Operation": 0x8,
        "Step": 0xA,
    },
}

PRIMITIVE_SIZES: dict[str, int] = {
    "bool": 1,
    "uint8_t": 1,
    "int8_t": 1,
    "uint16_t": 2,
    "int16_t": 2,
    "uint32_t": 4,
    "int32_t": 4,
    "uint64_t": 8,
    "int64_t": 8,
    "float": 4,
    "double": 8,
    "Il2CppMethodPointer": 8,
    "InvokerMethod": 8,
    "size_t": 8,
    "uintptr_t": 8,
    "il2cpp_array_size_t": 8,
    "il2cpp_array_lower_bound_t": 4,
}

DEFAULT_DUMPER_DIR = Path(
    r"c:\Users\chord\Documents\ForgeMaster\Miraesee\version\2.6.0\Il2CppDumper-net6-win-v6.7.46"
)
DEFAULT_METADATA = Path(
    r"c:\Users\chord\Documents\ForgeMaster\Miraesee\version\2.6.0\global-metadata.dat"
)


def align_up(value: int, alignment: int = ALIGNMENT) -> int:
    mask = alignment - 1
    return (value + mask) & ~mask


def hex_addr(value: int) -> str:
    return f"0x{value:X}"


@dataclass
class FieldLayout:
    name: str
    type_name: str
    offset: int
    size: int


class Il2CppHeaderParser:
    def __init__(self, header_text: str) -> None:
        self.header_text = header_text
        self.struct_fields: dict[str, list[tuple[str, str]]] = {}
        self._parse_structs()

    def _parse_structs(self) -> None:
        pattern = re.compile(
            r"struct\s+(\w+)\s*\{([^}]*)\}",
            re.MULTILINE | re.DOTALL,
        )
        for match in pattern.finditer(self.header_text):
            struct_name = match.group(1)
            body = match.group(2)
            fields: list[tuple[str, str]] = []
            in_union = False
            union_emitted = False
            for line in body.splitlines():
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                if line.startswith("union"):
                    in_union = True
                    union_emitted = False
                    continue
                if line == "};" or line == "}":
                    in_union = False
                    union_emitted = False
                    continue
                if in_union and union_emitted:
                    continue
                field_match = re.match(
                    r"(?:const\s+)?(?:struct\s+)?([\w\s\*]+?)\s+(\w+)\s*;",
                    line,
                )
                if not field_match:
                    continue
                type_name = field_match.group(1).strip()
                field_name = field_match.group(2)
                fields.append((field_name, type_name))
                if in_union:
                    union_emitted = True
            self.struct_fields[struct_name] = fields

    def _type_size(self, type_name: str, cache: dict[str, int]) -> int:
        if type_name in cache:
            return cache[type_name]
        base = type_name.replace("const ", "").strip()
        if base.endswith("*"):
            cache[type_name] = POINTER_SIZE
            return POINTER_SIZE
        if base in PRIMITIVE_SIZES:
            cache[type_name] = PRIMITIVE_SIZES[base]
            return PRIMITIVE_SIZES[base]
        if base == "Il2CppType":
            cache[type_name] = 16
            return 16
        if base.startswith("Il2CppRGCTXData"):
            cache[type_name] = POINTER_SIZE
            return POINTER_SIZE
        if base.startswith("VirtualInvokeData"):
            cache[type_name] = POINTER_SIZE * 2

        fields_name = f"{base}_Fields"
        if fields_name in self.struct_fields:
            size = self.layout_fields(fields_name).total_size
            cache[type_name] = size
            return size
        if base in self.struct_fields:
            size = self.layout_fields(base).total_size
            cache[type_name] = size
            return size

        if base.endswith("_o"):
            fields_name = base.replace("_o", "_Fields")
            if fields_name in self.struct_fields:
                size = self.layout_fields(fields_name).total_size
                cache[type_name] = size
                return size

        cache[type_name] = POINTER_SIZE
        return POINTER_SIZE

    @dataclass
    class StructLayout:
        struct_name: str
        fields: list[FieldLayout]
        total_size: int

    def layout_fields(self, struct_name: str) -> StructLayout:
        raw_fields = self.struct_fields.get(struct_name, [])
        offset = 0
        cache: dict[str, int] = {}
        laid_out: list[FieldLayout] = []
        for field_name, type_name in raw_fields:
            size = self._type_size(type_name, cache)
            offset = align_up(offset, min(ALIGNMENT, size) if size else ALIGNMENT)
            laid_out.append(FieldLayout(field_name, type_name, offset, size))
            offset += size
        total_size = align_up(offset)
        return self.StructLayout(struct_name, laid_out, total_size)

    def field_offset(self, struct_name: str, field_name: str) -> int | None:
        override = STRUCT_LAYOUT_OVERRIDES.get(struct_name, {}).get(field_name)
        if override is not None:
            return override
        layout = self.layout_fields(struct_name)
        for field in layout.fields:
            if field.name == field_name:
                return field.offset
        return None

    def struct_size(self, struct_name: str) -> int:
        return self.layout_fields(struct_name).total_size


class DumpCsParser:
    FIELD_RE = re.compile(
        r"^\s*(?:\[[\w\.]+\]\s*)*"
        r"(?:public|private|protected|internal)?\s*"
        r"(?:static\s+|readonly\s+|const\s+)*"
        r".+?\s+(\S+)\s*;\s*//\s*(0x[0-9A-Fa-f]+)",
        re.MULTILINE,
    )
    CLASS_RE = re.compile(
        r"(?:public|private|protected|internal)\s+(?:sealed\s+|abstract\s+)?"
        r"class\s+([\w\.]+(?:<[^>]+>)?)\s*(?::\s*[\w<>\.,\s]+)?\s*//\s*TypeDefIndex:\s*(\d+)",
    )

    def __init__(self, dump_text: str) -> None:
        self.dump_text = dump_text
        self.classes: dict[str, dict[str, Any]] = {}
        self._parse()

    def _parse(self) -> None:
        for class_match in self.CLASS_RE.finditer(self.dump_text):
            class_name = class_match.group(1)
            type_def_index = int(class_match.group(2))
            start = class_match.end()
            next_class = self.CLASS_RE.search(self.dump_text, start)
            end = next_class.start() if next_class else len(self.dump_text)
            block = self.dump_text[start:end]
            fields: dict[str, int] = {}
            for field_match in self.FIELD_RE.finditer(block):
                field_name = field_match.group(1)
                offset = int(field_match.group(2), 16)
                fields[field_name] = offset
            self.classes[class_name] = {
                "type_def_index": type_def_index,
                "fields": fields,
            }

    def field_offset(self, class_name: str, field_name: str) -> int | None:
        cls = self.classes.get(class_name)
        if not cls:
            return None
        return cls["fields"].get(field_name)


class ScriptJsonParser:
    def __init__(self, script: dict[str, Any]) -> None:
        self.script = script

    def script_method_rva(self, name_substr: str) -> int | None:
        for entry in self.script.get("ScriptMethod", []):
            if name_substr in entry.get("Name", ""):
                return entry["Address"]
        return None

    def metadata_address(self, name_substr: str) -> int | None:
        for entry in self.script.get("ScriptMetadata", []):
            if name_substr in entry.get("Name", ""):
                return entry["Address"]
        return None

    def metadata_method_slot(self, name_substr: str) -> int | None:
        for entry in self.script.get("ScriptMetadataMethod", []):
            if name_substr in entry.get("Name", ""):
                return entry["Address"]
        return None


def read_metadata_header(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError(f"{path} too small for metadata header")
    magic, version = struct.unpack_from("<II", data, 0)
    if magic != METADATA_MAGIC:
        raise ValueError(f"bad metadata magic {hex(magic)} in {path}")
    return {
        "path": str(path),
        "size_bytes": len(data),
        "magic": hex_addr(magic),
        "version": version,
    }


def ghidra_dat_addr(script_addr: int) -> str:
    return hex_addr(script_addr + 0x100000)


def build_calibration(
    dumper_dir: Path,
    metadata_path: Path,
) -> dict[str, Any]:
    il2cpp_h = (dumper_dir / "il2cpp.h").read_text(encoding="utf-8", errors="replace")
    dump_cs = (dumper_dir / "dump.cs").read_text(encoding="utf-8", errors="replace")
    script = json.loads((dumper_dir / "script.json").read_text(encoding="utf-8"))

    header = Il2CppHeaderParser(il2cpp_h)
    dump = DumpCsParser(dump_cs)
    script_parser = ScriptJsonParser(script)
    meta_header = read_metadata_header(metadata_path)

    klass1_size = IL2CPP_RUNTIME_LAYOUT["Il2CppClass_1_size"]
    il2cpp_class_offsets = dict(IL2CPP_RUNTIME_LAYOUT["Il2CppClass"])
    method_info_offsets = dict(IL2CPP_RUNTIME_LAYOUT["MethodInfo"])
    il2cpp_class_offsets_computed = {
        "static_fields": header.struct_size("Il2CppClass_1"),
        "rgctx_data": header.struct_size("Il2CppClass_1") + POINTER_SIZE,
    }
    method_info_offsets_computed = {
        key: header.field_offset("MethodInfo", key)
        for key in (
            "methodPointer",
            "virtualMethodPointer",
            "invoker_method",
            "name",
            "klass",
            "return_type",
            "parameters",
            "rgctx_data",
        )
    }
    rgctx_offsets = {
        "closed_klass_0": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__RGCTXs",
            "_0_Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel_",
        ),
        "inner_klass_1": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__RGCTXs",
            "_1_Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel_",
        ),
        "get_State_method": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__RGCTXs",
            "_2_Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__get_State",
        ),
        "get_Connection_method": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__RGCTXs",
            "_3_Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__get_Connection",
        ),
        "t_player_model_klass": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__RGCTXs",
            "_4_TPlayerModel",
        ),
        "get_PlayerModel_method": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__RGCTXs",
            "_5_Metaplay_Unity_DefaultIntegration_MetaplayClientState_GetPlayerModel_TPlayerModel_",
        ),
        "set_State_method": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__RGCTXs",
            "_6_Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__set_State",
        ),
    }
    static_fields_offsets = {
        "State": header.field_offset(
            "Metaplay_Unity_DefaultIntegration_MetaplayClientBase_TPlayerModel__StaticFields",
            "_State_k__BackingField",
        ),
    }

    journal_timeline_off = header.field_offset(
        "Metaplay_Core_Model_ModelJournal_Leader_IPlayerModelBase__Fields",
        "_timeline",
    )
    timeline_staged_model_off = header.field_offset(
        "Metaplay_Core_Model_Timeline_TModel__ModelJournal_Leader_StagedOp_TModel___ModelJournal_Leader_StagedStep_TModel___Fields",
        "_stagedModel",
    )

    forward_chain = {
        "object_header": IL2CPP_OBJECT_HEADER,
        "state_to_player_context": dump.field_offset(
            "MetaplayClientState",
            "<PlayerContext>k__BackingField",
        ),
        "ctx_to_player_journal": dump.field_offset(
            "DefaultPlayerClientContext",
            "_playerJournal",
        ),
        "journal_to_timeline": (
            IL2CPP_OBJECT_HEADER + journal_timeline_off
            if journal_timeline_off is not None
            else None
        ),
        "timeline_to_staged_model": (
            IL2CPP_OBJECT_HEADER + timeline_staged_model_off
            if timeline_staged_model_off is not None
            else None
        ),
    }

    player_model_fields = {
        "GamePaused": dump.field_offset("PlayerModel", "<GamePaused>k__BackingField"),
        "PlayerForgeModel": dump.field_offset("PlayerModel", "<PlayerForgeModel>k__BackingField"),
        "PlayerSkillCollectionModel": dump.field_offset(
            "PlayerModel",
            "<PlayerSkillCollectionModel>k__BackingField",
        ),
        "type_def_index": dump.classes.get("PlayerModel", {}).get("type_def_index"),
    }

    get_state_rva = script_parser.script_method_rva(
        "MetaplayClientBase<object>$$get_State"
    )
    get_player_model_rva = script_parser.script_method_rva(
        "MetaplayClientBase<object>$$get_PlayerModel"
    )

    closed_generic_methods = {
        "get_Connection": script_parser.metadata_method_slot(
            "MetaplayClientBase<PlayerModel>.get_Connection()"
        ),
        "get_PlayerContext": script_parser.metadata_method_slot(
            "MetaplayClientBase<PlayerModel>.get_PlayerContext()"
        ),
        "get_PlayerModel": script_parser.metadata_method_slot(
            "MetaplayClientBase<PlayerModel>.get_PlayerModel()"
        ),
    }

    type_info = {
        "MetaplayClientState": script_parser.metadata_address("MetaplayClientState_TypeInfo"),
        "PlayerModel": script_parser.metadata_address("Game.Logic.PlayerModel_TypeInfo"),
        "DefaultPlayerClientContext": script_parser.metadata_address(
            "DefaultPlayerClientContext_TypeInfo"
        ),
        "MetaplaySDK": script_parser.metadata_address("MetaplaySDK_TypeInfo"),
    }

    state_entry_recipe = {
        "description": "MetaplayClientBase<object>.get_State IL path",
        "steps": [
            "method_info = read(MethodInfo* at libil2cpp + method_table_slot)",
            "klass = read(method_info + klass_offset)",
            "if (klass.init_flags & 1) == 0: metadata init required (FUN_03db3610)",
            "rgctx = read(klass + rgctx_data_offset)",
            "inner = read(rgctx + inner_klass_1_offset)",
            "static_fields = read(inner + static_fields_offset)",
            "state = read(static_fields + State_offset)",
        ],
        "offsets": {
            "Il2CppClass.rgctx_data": il2cpp_class_offsets["rgctx_data"],
            "Il2CppClass.static_fields": il2cpp_class_offsets["static_fields"],
            "RGCTX.inner_klass_1": rgctx_offsets["inner_klass_1"],
            "StaticFields.State": static_fields_offsets["State"],
            "MethodInfo.klass": method_info_offsets["klass"],
        },
    }

    return {
        "version": "2.6.0",
        "sources": {
            "dumper_dir": str(dumper_dir),
            "metadata": meta_header,
        },
        "il2cpp_runtime": {
            "Il2CppClass_1_size": klass1_size,
            "Il2CppClass": {k: hex_addr(v) for k, v in il2cpp_class_offsets.items()},
            "MethodInfo": {k: hex_addr(v) for k, v in method_info_offsets.items()},
            "Il2CppClass_computed": {
                k: hex_addr(v) for k, v in il2cpp_class_offsets_computed.items()
            },
            "MethodInfo_computed": {
                k: hex_addr(v) if v is not None else None
                for k, v in method_info_offsets_computed.items()
            },
            "MetaplayClientBase_RGCTX": {
                k: hex_addr(v) for k, v in rgctx_offsets.items() if v is not None
            },
            "MetaplayClientBase_StaticFields": {
                k: hex_addr(v) for k, v in static_fields_offsets.items() if v is not None
            },
        },
        "methods": {
            "get_State": {
                "code_rva": hex_addr(get_state_rva) if get_state_rva else None,
                "open_generic_inst": "MetaplayClientBase<object>",
            },
            "get_PlayerModel": {
                "code_rva": hex_addr(get_player_model_rva) if get_player_model_rva else None,
                "open_generic_inst": "MetaplayClientBase<object>",
            },
        "closed_generic_MetaplayClientBase_PlayerModel": {
            k: {
                "script_metadata_slot": hex_addr(v),
                "ghidra_dat_guess": ghidra_dat_addr(v),
            }
            for k, v in closed_generic_methods.items()
            if v is not None
        },
        "method_table_slots": {
            "get_State": hex_addr(0x763E80),
            "get_PlayerModel": hex_addr(0x763E50),
        },
    },
        "type_info": {k: hex_addr(v) if v else None for k, v in type_info.items()},
        "forward_chain": {k: hex_addr(v) if isinstance(v, int) else v for k, v in forward_chain.items()},
        "player_model": {k: hex_addr(v) if isinstance(v, int) else v for k, v in player_model_fields.items()},
        "state_entry_recipe": state_entry_recipe,
        "verified_expectations": {
            "forward_chain": {
                "state_to_player_context": "0x10",
                "ctx_to_player_journal": "0x78",
                "journal_to_timeline": "0x18",
                "timeline_to_staged_model": "0x60",
            },
            "Il2CppClass": {"rgctx_data": "0xC0", "static_fields": "0xB8"},
            "MethodInfo.klass": "0x20",
        },
    }


def print_summary(cal: dict[str, Any]) -> None:
    meta = cal["sources"]["metadata"]
    print(f"global-metadata.dat v{meta['version']} ({meta['size_bytes']:,} bytes)")
    print()
    print("=== Il2Cpp runtime offsets ===")
    runtime = cal["il2cpp_runtime"]
    print(f"  Il2CppClass_1_size: {hex_addr(runtime['Il2CppClass_1_size'])}")
    for section in ("Il2CppClass", "MethodInfo", "MetaplayClientBase_RGCTX", "MetaplayClientBase_StaticFields"):
        print(f"  {section}:")
        for key, val in runtime[section].items():
            print(f"    {key}: {val}")
    print()
    print("=== Methods ===")
    for name, info in cal["methods"].items():
        if name == "closed_generic_MetaplayClientBase_PlayerModel":
            print(f"  {name}:")
            for mname, minfo in info.items():
                print(f"    {mname}: slot={minfo['script_metadata_slot']} ghidra={minfo['ghidra_dat_guess']}")
            continue
        print(f"  {name}: code_rva={info.get('code_rva')} ({info.get('open_generic_inst')})")
    print()
    print("=== Forward chain (instance offsets) ===")
    for key, val in cal["forward_chain"].items():
        exp = cal["verified_expectations"]["forward_chain"].get(key)
        mark = "OK" if val == exp else f"EXPECTED {exp}"
        print(f"  {key}: {val}  [{mark}]")
    print()
    print("=== TypeInfo script.json addresses ===")
    for name, addr in cal["type_info"].items():
        print(f"  {name}: {addr}")
    print()
    print("=== PlayerModel probe fields ===")
    for key, val in cal["player_model"].items():
        print(f"  {key}: {val}")


def write_calibration_txt(cal: dict[str, Any], path: Path) -> None:
    runtime = cal["il2cpp_runtime"]
    mi = runtime["MethodInfo"]
    klass = runtime["Il2CppClass"]
    rgctx = runtime["MetaplayClientBase_RGCTX"]
    static_fields = runtime["MetaplayClientBase_StaticFields"]
    chain = cal["forward_chain"]
    player = cal["player_model"]
    methods = cal["methods"]
    closed = methods.get("closed_generic_MetaplayClientBase_PlayerModel", {})
    table_slots = methods.get("method_table_slots", {})
    meta = cal["sources"]["metadata"]

    def hx(key: str, blob: dict[str, Any]) -> str:
        val = blob.get(key)
        if val is None:
            return ""
        if isinstance(val, str):
            return val[2:].upper() if val.startswith("0x") else val.upper()
        return format(int(val), "X")

    lines = [
        f"version={cal['version']}",
        f"metadata_version={meta['version']}",
        f"rva_get_state={hx('code_rva', methods.get('get_State', {}))}",
        f"rva_get_player_model={hx('code_rva', methods.get('get_PlayerModel', {}))}",
        f"rva_method_table_get_state={hx('get_State', table_slots)}",
        f"rva_method_table_get_player_model={hx('get_PlayerModel', table_slots)}",
        f"off_mi_klass={hx('klass', mi)}",
        f"off_mi_rgctx={hx('rgctx_data', mi)}",
        f"off_klass_rgctx={hx('rgctx_data', klass)}",
        f"off_klass_static_fields={hx('static_fields', klass)}",
        f"off_rgctx_inner_klass={hx('inner_klass_1', rgctx)}",
        f"off_rgctx_mid_holder={hx('get_State_method', rgctx)}",
        f"off_rgctx_mid_klass={hx('t_player_model_klass', rgctx)}",
        f"off_static_state={hx('State', static_fields)}",
        f"off_state_player_context={hx('state_to_player_context', chain)}",
        f"off_ctx_journal={hx('ctx_to_player_journal', chain)}",
        f"off_journal_timeline={hx('journal_to_timeline', chain)}",
        f"off_timeline_staged={hx('timeline_to_staged_model', chain)}",
        f"off_player_game_paused={hx('GamePaused', player)}",
        f"off_player_forge={hx('PlayerForgeModel', player)}",
        f"off_player_skill_col={hx('PlayerSkillCollectionModel', player)}",
        f"slot_get_connection={hx('ghidra_dat_guess', closed.get('get_Connection', {}))}",
        f"slot_get_player_context={hx('ghidra_dat_guess', closed.get('get_PlayerContext', {}))}",
        f"slot_get_player_model={hx('ghidra_dat_guess', closed.get('get_PlayerModel', {}))}",
        f"typeinfo_metaplay_client_state={hx('MetaplayClientState', cal['type_info'])}",
        f"typeinfo_player_model={hx('PlayerModel', cal['type_info'])}",
        f"typeinfo_default_player_context={hx('DefaultPlayerClientContext', cal['type_info'])}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dumper-dir", type=Path, default=DEFAULT_DUMPER_DIR)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "miraesee_il2cpp_calibration.json",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    cal = build_calibration(args.dumper_dir, args.metadata)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(cal, indent=2), encoding="utf-8")
    txt_path = args.output.with_suffix(".txt")
    write_calibration_txt(cal, txt_path)
    if not args.quiet:
        print_summary(cal)
        print(f"\nWrote {args.output}")
        print(f"Wrote {txt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
