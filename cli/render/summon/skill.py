from cli.render.summon.split_view import render_split


def render(pulls: list, count: int) -> list[str]:
    return render_split("SKILL SUMMON", pulls, "skill", count)
