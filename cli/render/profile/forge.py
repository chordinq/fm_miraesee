from cli.render.equipment import render_equipment

def render(session) -> list[str]:
    return render_equipment(session)
