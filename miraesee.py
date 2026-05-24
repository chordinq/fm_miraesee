import os
import sys
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from utils.constants import get_padded_kor, UI_COLORS, COLOR_RESET

def parse_state_val(hex_str):
    val = int(hex_str, 16)
    return (val >> 32) & 0xFFFFFFFF, val & 0xFFFFFFFF

def get_max_count(mode, level_idx):
    try:
        if mode == "Skill": path = 'configs/SkillSummonConfig.json'
        elif mode in ["Pet", "Egg"]: path = 'configs/EggSummonConfig.json'
        elif mode == "Mount": path = 'configs/MountSummonConfig.json'
        else: return 999
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        levels = data.get("Levels", [])
        return levels[min(level_idx, len(levels) - 1)].get("SummonsRequired", 999)
    except FileNotFoundError: return 999

def initialize_state():
    state = {
        "Forge": {"seed": 0, "level": 0, "chance": 0.0, "is_ascended": False, "ascension_level": 0, "history": []},
        "Skill": {"seed": 0, "level": 0, "count": 0, "chance": 0.0, "is_ascended": False, "ascension_level": 0, "history": []},
        "Pet": {"seed": 0, "level": 0, "count": 0, "chance": 0.0, "is_ascended": False, "ascension_level": 0, "history": []},
        "Mount": {"seed": 0, "level": 0, "count": 0, "chance": 0.0, "is_ascended": False, "ascension_level": 0, "history": []},
        "current_mode": "Global",
        "tutorial_step": 0,
        "tutorial_target_tier_kor": "양자",
        "tutorial_target_tier_eng": "quantum",
        "tutorial_target_tier_m1_kor": "다중우주",
        "tutorial_target_tier_m1_eng": "multiverse",
        "tutorial_next_level": 20
    }
    
    print("\n게임가디언에서 복사한 12줄의 HEX 코드를 붙여넣고 엔터를 누르세요:")
    lines = []
    while len(lines) < 12:
        line = input().strip()
        if line: lines.append(line)
            
    print("\n추가 보너스 확률(%)을 입력하세요 (숫자만 입력, 없으면 그냥 엔터):")
    f_chance = input(f"- {UI_COLORS['Forge']}대장간{COLOR_RESET} 무료 제작 확률 (%) : ").strip()
    p_chance = input(f"- {UI_COLORS['Pet']}펫{COLOR_RESET} 추가 소환 확률 (%)     : ").strip()
    m_chance = input(f"- {UI_COLORS['Mount']}탈것{COLOR_RESET} 추가 소환 확률 (%)   : ").strip()

    state["Forge"]["seed"] = int(lines[0], 16)
    state["Forge"]["level"] = int(lines[1], 16) + 1 
    state["Forge"]["ascension_level"] = int(lines[2], 16)
    state["Forge"]["is_ascended"] = state["Forge"]["ascension_level"] > 0
    state["Forge"]["chance"] = float(f_chance) if f_chance else 0.0
    
    state["Skill"]["seed"] = int(lines[3], 16)
    state["Skill"]["level"], state["Skill"]["count"] = parse_state_val(lines[4])
    state["Skill"]["ascension_level"] = int(lines[5], 16)
    state["Skill"]["is_ascended"] = state["Skill"]["ascension_level"] > 0
    state["Skill"]["chance"] = 0.0
    
    state["Pet"]["seed"] = int(lines[6], 16)
    state["Pet"]["level"], state["Pet"]["count"] = parse_state_val(lines[7])
    state["Pet"]["ascension_level"] = int(lines[8], 16)
    state["Pet"]["is_ascended"] = state["Pet"]["ascension_level"] > 0
    state["Pet"]["chance"] = float(p_chance) if p_chance else 0.0
    
    state["Mount"]["seed"] = int(lines[9], 16)
    state["Mount"]["level"], state["Mount"]["count"] = parse_state_val(lines[10])
    state["Mount"]["ascension_level"] = int(lines[11], 16)
    state["Mount"]["is_ascended"] = state["Mount"]["ascension_level"] > 0
    state["Mount"]["chance"] = float(m_chance) if m_chance else 0.0
    
    for mode in ["Forge", "Skill", "Pet", "Mount"]:
        state[mode]["history"].clear()
        state[mode]["init_seed"], state[mode]["init_level"] = state[mode]["seed"], state[mode]["level"]
        state[mode]["init_chance"] = state[mode]["chance"]
        if "count" in state[mode]: state[mode]["init_count"] = state[mode]["count"]

    print("\n초기화 완료! (승천 여부가 자동으로 적용되었습니다)")
    
    f_lvl = f"Level: {state['Forge']['level']:>2}"
    s_lvl = f"Level: {state['Skill']['level']+1:>2}({state['Skill']['count']:>3}/{get_max_count('Skill', state['Skill']['level']):>3})"
    p_lvl = f"Level: {state['Pet']['level']+1:>2}({state['Pet']['count']:>3}/{get_max_count('Pet', state['Pet']['level']):>3})"
    m_lvl = f"Level: {state['Mount']['level']+1:>2}({state['Mount']['count']:>3}/{get_max_count('Mount', state['Mount']['level']):>3})"

    f_asc = min(4, max(0, state['Forge']['ascension_level']))
    s_asc = min(4, max(0, state['Skill']['ascension_level']))
    p_asc = min(4, max(0, state['Pet']['ascension_level']))
    m_asc = min(4, max(0, state['Mount']['ascension_level']))

    f_stars = "★" * f_asc + "☆" * (4 - f_asc)
    s_stars = "★" * s_asc + "☆" * (4 - s_asc)
    p_stars = "★" * p_asc + "☆" * (4 - p_asc)
    m_stars = "★" * m_asc + "☆" * (4 - m_asc)

    print(f"{UI_COLORS['Forge']}[ Forge ]{COLOR_RESET} | {f_lvl:<18} | Ascension: {f_stars} | Chance: {state['Forge']['chance']:>4.1f}% | Seed: {state['Forge']['seed']:016X}")
    print(f"{UI_COLORS['Skill']}[ Skill ]{COLOR_RESET} | {s_lvl:<18} | Ascension: {s_stars} | Chance:  0.0% | Seed: {state['Skill']['seed']:016X}")
    print(f"{UI_COLORS['Pet']}[  Pet  ]{COLOR_RESET} | {p_lvl:<18} | Ascension: {p_stars} | Chance: {state['Pet']['chance']:>4.1f}% | Seed: {state['Pet']['seed']:016X}")
    print(f"{UI_COLORS['Mount']}[ Mount ]{COLOR_RESET} | {m_lvl:<18} | Ascension: {m_stars} | Chance: {state['Mount']['chance']:>4.1f}% | Seed: {state['Mount']['seed']:016X}")
    
    return state


def get_command_schema(mode):
    base = {
        "mode": ["forge", "skill", "pet", "mount"],
        "tutorial": [],
        "report": ["all"],
        "status": [],
        "reset": ["all"],
        "return": [],
        "exit": [],
        "help": [],
        "save": [],
        "load": []
    }
    if mode == "Forge":
        base.update({
            "forge": ["amount:", "times:"],
            "search": ["tier:", "perf:", "type:", "stat:"],
            "set": ["level:", "chance:"]
        })
    elif mode == "Skill":
        base.update({
            "summon": ["amount:", "times:"],
            "search": ["tier:"],
            "set": ["level:"]
        })
    elif mode in ["Pet", "Mount"]:
        base.update({
            "summon": ["amount:", "times:"],
            "search": ["tier:", "perf:", "stat:"],
            "optimize": ["amount:", "mode:", "tier:"],
            "set": ["chance:"]
        })
    return base


class SmartCompleter(Completer):
    def __init__(self, state):
        self.state = state
        self.forge_tiers = [
            ("primitive", "#f1f1f1", "원시"), ("medieval", "#5dd8ff", "중세"),
            ("early-modern", "#5dff8a", "근대초기"), ("modern", "#fcff5d", "현대"),
            ("space", "#ff5d5d", "우주"), ("interstellar", "#d55dff", "항성"),
            ("multiverse", "#75ffee", "다중우주"), ("quantum", "#7d5dff", "양자"),
            ("underworld", "#b07879", "지하세계"), ("divine", "#ff9e0d", "신성")
        ]
        self.other_tiers = [
            ("common", "#f1f1f1", "일반"), ("rare", "#5dd8ff", "희귀"),
            ("epic", "#5dff8a", "서사"), ("legendary", "#fcff5d", "전설"),
            ("ultimate", "#ff5d5d", "궁극"), ("mythic", "#d55dff", "신화")
        ]
        self.types = ["melee", "ranged", "weapon", "helmet", "armour", "gloves", "shoes", "belt", "necklace", "ring"]
        self.stats_options = [
            ("health", "체력"), ("damage", "공격력"), ("skilldamage", "스킬 피해"), 
            ("healthregen", "체력 재생"), ("meleedamage", "근거리 피해"), 
            ("rangeddamage", "원거리 피해"), ("attackspeed", "공격 속도"), 
            ("criticalchance", "치명타 확률"), ("criticaldamage", "치명타 피해"), 
            ("doublechance", "더블 확률"), ("lifesteal", "생명력 흡수"), 
            ("blockchance", "막기 확률"), ("skillcooldown", "스킬 쿨다운")
        ]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()
        current_word = "" if text.endswith(' ') else (words[-1] if words else "")
        mode = self.state["current_mode"]
        schema = get_command_schema(mode)
        cmd = words[0].lower() if words else ""
        
        if len(words) == 0 or (len(words) == 1 and not text.endswith(' ')):
            for k in schema.keys():
                if k.startswith(current_word.lower()):
                    yield Completion(k, start_position=-len(current_word))
            return

        if len(words) >= 1 and cmd in schema and not ':' in current_word:
            for param in schema[cmd]:
                if param.startswith(current_word.lower()) and param not in text:
                    yield Completion(param, start_position=-len(current_word))

        if current_word.startswith("tier:"):
            val = current_word[len("tier:"):].lower()
            if mode == "Forge" or mode == "Global":
                for t_eng, t_color, t_kor in self.forge_tiers:
                    if t_eng.startswith(val):
                        display_html = HTML(f'<style fg="{t_color}">{t_eng} ({t_kor})</style>')
                        yield Completion(t_eng, start_position=-len(val), display=display_html)
            else:
                for r_eng, r_color, r_kor in self.other_tiers:
                    if r_eng.startswith(val):
                        display_html = HTML(f'<style fg="{r_color}">{r_eng} ({r_kor})</style>')
                        yield Completion(r_eng, start_position=-len(val), display=display_html)
        
        elif current_word.startswith("type:") and mode == "Forge":
            val = current_word[len("type:"):].lower()
            for t in self.types:
                if t.startswith(val): yield Completion(t, start_position=-len(val))
                
        elif current_word.startswith("stat:"):
            parts = current_word.split(":")
            if len(parts) == 2:
                val = parts[1].lower().replace("_", "").replace(" ", "")
                for s_eng, s_kor in self.stats_options:
                    if s_eng.startswith(val):
                        display_html = HTML(f'<style fg="#5dd8ff">{s_eng} ({s_kor})</style>')
                        yield Completion(s_eng, start_position=-len(val), display=display_html)
                        
        elif current_word.startswith("mode:") and cmd == "optimize":
            val = current_word[len("mode:"):].lower()
            for opt in ["bonus", "stat", "shortcut"]:
                if opt.startswith(val):
                    yield Completion(opt, start_position=-len(val))


class SmartSuggester(AutoSuggest):
    def __init__(self, state):
        self.state = state

    def get_suggestion(self, buffer, document):
        text = document.text
        mode = self.state["current_mode"]
        
        from utils.tutorial import get_tutorial_suggestion
        tut = get_tutorial_suggestion(self.state, text)
        if tut: return Suggestion(tut)
        
        if not text: return None
        
        if text.lower() == "r": return Suggestion("eturn")
        if text.lower() == "q": return Suggestion("uit")
        if text.lower() == "t": return Suggestion("utorial")
        
        parts = text.split()
        cmd = parts[0].lower() if parts else ""
        schema = get_command_schema(mode)

        if len(parts) == 1 and not text.endswith(" "):
            for k in schema.keys():
                if k.startswith(text.lower()): return Suggestion(k[len(text):])
        
        if text.endswith(" ") and cmd in schema:
            for param in schema[cmd]:
                if param == "stat:": return Suggestion(param)
                if param not in text: return Suggestion(param)
                    
        if text.endswith("amount:"):
            step = self.state.get("tutorial_step", 0)
            if step == 2: return Suggestion("3")
            if step == 3: return Suggestion("10000")
        elif text.endswith("tier:"):
            if self.state.get("tutorial_step") == 5:
                return Suggestion(self.state.get('tutorial_target_tier_eng', 'quantum'))
        elif text.endswith("type:"): return Suggestion("all")
        
        elif "mode:" in text and cmd == "optimize":
            for p in parts:
                if p.startswith("mode:"):
                    val = p[len("mode:"):]
                    if "bonus".startswith(val) and val != "bonus": return Suggestion("bonus"[len(val):])
                    if "stat".startswith(val) and val != "stat": return Suggestion("stat"[len(val):])
                    if "shortcut".startswith(val) and val != "shortcut": return Suggestion("shortcut"[len(val):])
                    
        return None

def setup_ui(state):
    bindings = KeyBindings()
    
    @bindings.add('tab')
    def _(event):
        b = event.current_buffer
        
        if not b.text:
            step = state.get("tutorial_step", 0)
            mode = state["current_mode"]
            if step == 0 and mode == "Global":
                b.insert_text('tutorial')
                return
            
            from utils.tutorial import get_tutorial_suggestion
            tut_target = get_tutorial_suggestion(state, "")
            if tut_target:
                if ' ' in tut_target: b.insert_text(tut_target.split(' ', 1)[0])
                else: b.insert_text(tut_target)
                return

        if b.complete_state:
            b.complete_next()
        elif b.suggestion and b.document.is_cursor_at_the_end:
            sug_text = b.suggestion.text
            if ' ' in sug_text: b.insert_text(sug_text.split(' ', 1)[0])
            else: b.insert_text(sug_text)
        else:
            b.start_completion(select_first=True)

    return PromptSession(
        completer=SmartCompleter(state),
        auto_suggest=SmartSuggester(state),
        key_bindings=bindings,
        complete_while_typing=False
    )

def get_user_input(session, state):
    mode = state["current_mode"]
    step = state.get("tutorial_step", 0)
    
    ph = ""
    if step == 0 and mode == "Global": ph = "tutorial"
    elif step == 1 and mode == "Global": ph = "mode forge"
    elif step == 2 and mode == "Forge": ph = "forge amount:3"
    elif step == 4 and mode == "Forge": ph = "report"
    elif step == 5 and mode == "Forge": ph = f"search tier:{state.get('tutorial_target_tier_eng', 'quantum')}"
    elif step == 6 and mode == "Forge": ph = f"search tier:{state.get('tutorial_target_tier_m1_eng', 'multiverse')} stat:attackspeed:90"
    elif step == 7 and mode == "Forge": ph = "reset"
    elif step == 9 and mode == "Forge": ph = f"set level:{state.get('tutorial_next_level', 20)}"
    
    if mode == "Global": prompt_html = HTML(f'\n<ansigray>></ansigray> ')
    elif mode == "Forge": prompt_html = HTML(f'\n<ansiwhite>[Forge]</ansiwhite> > ')
    elif mode == "Skill": prompt_html = HTML(f'\n<ansigreen>[Skill]</ansigreen> > ')
    elif mode == "Pet": prompt_html = HTML(f'\n<ansiblue>[Pet]</ansiblue> > ')
    elif mode == "Mount": prompt_html = HTML(f'\n<ansiyellow>[Mount]</ansiyellow> > ')
        
    try: return session.prompt(prompt_html, placeholder=ph).strip()
    except KeyboardInterrupt: return ""
    except EOFError: return None

def main():
    os.system("")
    print("="*60)
    print("ForgeMaster 미래시 시뮬레이터")
    print("="*60)
    
    session_state = initialize_state()
    session = setup_ui(session_state)
    from utils.commands import execute_command
    
    while True:
        cmd_input = get_user_input(session, session_state)
        
        if cmd_input is None: break
        if not cmd_input: continue
            
        should_continue = execute_command(session_state, cmd_input)
        if not should_continue: break

if __name__ == "__main__":
    main()