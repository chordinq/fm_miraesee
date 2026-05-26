# cli/store/query.py
"""Query / filter engine for the summon store."""

from __future__ import annotations
import sqlite3

from cli.store.models import RARITY_ORDER, SummonFilter, SummonRecord


def query_records(
    conn: sqlite3.Connection,
    f: SummonFilter,
) -> list[SummonRecord]:
    conds: list[str] = []
    params: list = []

    if f.kind:
        conds.append("kind = ?"); params.append(f.kind)

    if f.session_id:
        conds.append("session_id = ?"); params.append(f.session_id)

    if f.is_bonus is not None:
        conds.append("is_bonus = ?"); params.append(1 if f.is_bonus else 0)

    if f.pet_type:
        conds.append("pet_type = ?"); params.append(f.pet_type)

    if f.name_contains:
        conds.append("name LIKE ?"); params.append(f"%{f.name_contains}%")

    if f.min_rarity:
        cutoff = RARITY_ORDER.get(f.min_rarity, 0)
        rarities = [k for k, v in RARITY_ORDER.items() if v >= cutoff]
        ph = ",".join("?" for _ in rarities)
        conds.append(f"rarity IN ({ph})"); params.extend(rarities)

    if f.min_perf is not None:
        conds.append("(stat1_perf >= ? OR stat2_perf >= ?)")
        params.extend([f.min_perf, f.min_perf])

    if f.max_perf is not None:
        conds.append("(stat1_perf <= ? AND (stat2_perf IS NULL OR stat2_perf <= ?))")
        params.extend([f.max_perf, f.max_perf])

    if f.min_val is not None:
        conds.append("(stat1_val >= ? OR stat2_val >= ?)")
        params.extend([f.min_val, f.min_val])

    if f.max_val is not None:
        conds.append("(stat1_val <= ? AND (stat2_val IS NULL OR stat2_val <= ?))")
        params.extend([f.max_val, f.max_val])

    # ALL listed types must be present (each adds one condition)
    for st in f.stat_types:
        conds.append("(stat1_type = ? OR stat2_type = ?)"); params.extend([st, st])

    # ANY listed types
    if f.any_stat_types:
        ph = ",".join("?" for _ in f.any_stat_types)
        conds.append(f"(stat1_type IN ({ph}) OR stat2_type IN ({ph}))")
        params.extend(f.any_stat_types * 2)

    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    sql = f"SELECT * FROM summon_records {where} ORDER BY {f.order_by} LIMIT ? OFFSET ?"
    params.extend([f.limit, f.offset])

    return [_row(r) for r in conn.execute(sql, params).fetchall()]


def count_records(conn: sqlite3.Connection, f: SummonFilter) -> int:
    """Count matching records (no LIMIT/OFFSET)."""
    f2 = SummonFilter(
        kind=f.kind, session_id=f.session_id, min_rarity=f.min_rarity,
        stat_types=f.stat_types, any_stat_types=f.any_stat_types,
        min_perf=f.min_perf, max_perf=f.max_perf,
        min_val=f.min_val, max_val=f.max_val,
        pet_type=f.pet_type, is_bonus=f.is_bonus,
        name_contains=f.name_contains,
        limit=999_999_999, offset=0, order_by="id",
    )
    conds: list[str] = []
    params: list = []
    if f2.kind:
        conds.append("kind = ?"); params.append(f2.kind)
    if f2.session_id:
        conds.append("session_id = ?"); params.append(f2.session_id)
    if f2.min_rarity:
        cutoff = RARITY_ORDER.get(f2.min_rarity, 0)
        rarities = [k for k, v in RARITY_ORDER.items() if v >= cutoff]
        ph = ",".join("?" for _ in rarities)
        conds.append(f"rarity IN ({ph})"); params.extend(rarities)
    if f2.min_perf is not None:
        conds.append("(stat1_perf >= ? OR stat2_perf >= ?)"); params.extend([f2.min_perf, f2.min_perf])
    if f2.stat_types:
        for st in f2.stat_types:
            conds.append("(stat1_type = ? OR stat2_type = ?)"); params.extend([st, st])
    if f2.any_stat_types:
        ph = ",".join("?" for _ in f2.any_stat_types)
        conds.append(f"(stat1_type IN ({ph}) OR stat2_type IN ({ph}))"); params.extend(f2.any_stat_types * 2)
    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    row = conn.execute(f"SELECT COUNT(*) FROM summon_records {where}", params).fetchone()
    return row[0] if row else 0


def _row(r: sqlite3.Row) -> SummonRecord:
    return SummonRecord(
        id=r["id"], session_id=r["session_id"], dump_hash=r["dump_hash"],
        kind=r["kind"], batch_ts=r["batch_ts"],
        pull_global_idx=r["pull_global_idx"], pull_batch_idx=r["pull_batch_idx"],
        rarity=r["rarity"], name=r["name"], is_bonus=bool(r["is_bonus"]),
        stat1_type=r["stat1_type"], stat1_perf=r["stat1_perf"], stat1_val=r["stat1_val"],
        stat2_type=r["stat2_type"], stat2_perf=r["stat2_perf"], stat2_val=r["stat2_val"],
        egg_seed=r["egg_seed"], pet_idx=r["pet_idx"], pet_type=r["pet_type"],
    )
