from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SummonOutcome:
    success: bool
    pulls: list
    error: str = ""
    kind: str = ""


def run_summon(session, kind: str, count: int) -> SummonOutcome:
    gl = session.game_logic
    fn = {"skill": gl.summon_skills, "egg": gl.summon_eggs, "mount": gl.summon_mounts}.get(kind)
    if not fn:
        return SummonOutcome(False, [], f"unknown kind {kind}", kind)
    result = fn(count)
    if not result.success:
        return SummonOutcome(False, [], result.error or "failed", kind)
    pulls = result.pulls or []
    if pulls:
        session.history.add(kind, count, pulls)
        _persist(session, kind, pulls)
    return SummonOutcome(True, pulls, "", kind)


def _persist(session, kind: str, pulls: list) -> None:
    try:
        db = getattr(session, "db", None)
        if not db:
            return
        from cli.store.database import save_batch, dump_hash
        save_batch(db, session_id=session.session_id, dump_hash_=dump_hash(session.dump_raw), kind=kind, pulls=pulls)
    except Exception:
        pass
