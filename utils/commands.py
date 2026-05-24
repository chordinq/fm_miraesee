import os
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from utils.constants import get_padded_kor, UI_COLORS, COLOR_RESET

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

def save_state(state, name):
    os.makedirs("saves", exist_ok=True)
    with open(f"saves/{name}.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)
    print(f"'{name}'(으)로 상태가 저장되었습니다.")

def load_state(state, name):
    try:
        with open(f"saves/{name}.json", "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
            for mode in ["Forge", "Skill", "Pet", "Mount"]:
                if mode in loaded_data:
                    for i, item in enumerate(loaded_data[mode].get("history", [])):
                        if "index" not in item:
                            item["index"] = i + 1
            state.update(loaded_data)
        print(f"'{name}' 상태를 성공적으로 불러왔습니다.")
    except FileNotFoundError:
        print(f"'{name}' 세이브 파일을 찾을 수 없습니다.")

def print_report_all(state):
    from utils.constants import RARITY_KOR, RARITY_COLOR, AGE_NAME, AGE_KOR_SPACED, AGE_COLOR, COLOR_RESET
    print("\n" + "="*80)
    print(" 📊 미래시 통합 대시보드 (Report All)")
    print("="*80)
    for mode in ["Forge", "Skill", "Pet", "Mount"]:
        s = state[mode]
        history = s["history"]
        total = len(history)
        if mode == "Forge":
            print(f"\n{UI_COLORS['Forge']}[ ⚒️ 대장간 (Forge) ]{COLOR_RESET} - Lv {s['level']} | 총 제작: {total}회")
            if not history: print("  - 기록 없음")
            else:
                best = max(history, key=lambda x: (x['Age'], x['Perf']))
                kor_name = get_padded_kor(AGE_KOR_SPACED[best['Age']], 8)
                c_age = f"{AGE_COLOR.get(best['Age'], COLOR_RESET)}[{kor_name.strip()}]{COLOR_RESET}"
                from utils.constants import TYPE_KOR_SPACED
                kor_type = TYPE_KOR_SPACED.get(best['Type'], best['Type'])
                stats = ", ".join([f"{ds['name']} +{ds['value']:.2f}%" for ds in best['DetailedStats']])
                print(f"  🏆 최고 획득: {c_age} {kor_type} | {stats} (평균 {best['Perf']:.2f}%)")
        elif mode == "Skill":
            print(f"\n{UI_COLORS['Skill']}[ 🪄 스킬 (Skill) ]{COLOR_RESET} - Lv {s['level']+1} | 총 소환: {total}회")
            if not history: print("  - 기록 없음")
            else:
                best = max(history, key=lambda x: x['rarity_score'])
                r_name = best['rarity_name']
                aligned_r = f"[{RARITY_KOR[r_name]}]"
                c_r = f"{RARITY_COLOR[r_name]}{aligned_r}{COLOR_RESET}"
                print(f"  🏆 최고 획득: {c_r} {best['skill_name']}")
        elif mode == "Pet":
            print(f"\n{UI_COLORS['Pet']}[ 🥚 펫 (Egg/Pet) ]{COLOR_RESET} - Lv {s['level']+1} | 총 부화: {total}마리")
            if not history: print("  - 기록 없음")
            else:
                best = max(history, key=lambda x: (x['rarity_score'], x['perfection']))
                r_name = best['rarity_name']
                aligned_r = f"[{RARITY_KOR[r_name]}]"
                c_r = f"{RARITY_COLOR[r_name]}{aligned_r}{COLOR_RESET}"
                stats = ", ".join([f"{ds['name']} +{ds['value']:.2f}%" for ds in best['detailed_stats']])
                print(f"  🏆 최고 획득: {c_r} {best['pet_type']} | {stats} (평균 {best['perfection']:.2f}%)")
        elif mode == "Mount":
            print(f"\n{UI_COLORS['Mount']}[ 🐎 탈것 (Mount) ]{COLOR_RESET} - Lv {s['level']+1} | 총 소환: {total}마리")
            if not history: print("  - 기록 없음")
            else:
                best = max(history, key=lambda x: (x['rarity_score'], x['perfection']))
                r_name = best['rarity_name']
                aligned_r = f"[{RARITY_KOR[r_name]}]"
                c_r = f"{RARITY_COLOR[r_name]}{aligned_r}{COLOR_RESET}"
                stats = ", ".join([f"{ds['name']} +{ds['value']:.2f}%" for ds in best['detailed_stats']])
                print(f"  🏆 최고 획득: {c_r} | {stats} (평균 {best['perfection']:.2f}%)")
    print("="*80)

def handle_set_command(state, mode, args):
    if mode == "Global":
        print("기본 모드에서는 변수를 조작할 수 없습니다. 'mode [모듈명]'으로 진입한 후 사용해주세요.")
        return True
    
    if not args:
        print("사용법: set [속성]:[값] (예: set level:20)")
        return True
        
    for arg in args:
        if ":" not in arg:
            print(f"경고: 잘못된 형식입니다 -> '{arg}'. 반드시 '속성:값' 형태로 입력하세요. (예: level:20)")
            continue
            
        key, val_str = arg.split(":", 1)
        key = key.lower()
        
        try: val = float(val_str) if '.' in val_str else int(val_str)
        except ValueError:
            print(f"'{val_str}'은(는) 유효한 숫자가 아닙니다.")
            continue
            
        if mode == "Forge":
            if key not in ["level", "chance"]:
                print("[Forge] 'level:' 또는 'chance:' 속성만 변경할 수 있습니다.")
                continue
            state["Forge"][key] = val
            print(f"{UI_COLORS['Forge']}[Forge]{COLOR_RESET} {key} 값이 {val}(으)로 변경되었습니다.")
        elif mode == "Skill":
            if key != "level":
                print("[Skill] 'level:' 속성만 변경할 수 있습니다.")
                continue
            state["Skill"][key] = val
            print(f"{UI_COLORS['Skill']}[Skill]{COLOR_RESET} {key} 값이 {val}(으)로 변경되었습니다.")
        elif mode in ["Pet", "Mount"]:
            if key != "chance":
                print(f"[{mode}] 'chance:' 속성만 변경할 수 있습니다.")
                continue
            state[mode][key] = val
            print(f"{UI_COLORS[mode]}[{mode}]{COLOR_RESET} chance 값이 {val}(으)로 변경되었습니다.")
            
    return True

def handle_reset_command(state, mode, args):
    target = args[0].lower() if args else ""
    def _reset_module(m):
        state[m]["seed"] = state[m].get("init_seed", state[m]["seed"])
        state[m]["level"] = state[m].get("init_level", state[m]["level"])
        state[m]["chance"] = state[m].get("init_chance", state[m]["chance"])
        if "count" in state[m]: state[m]["count"] = state[m].get("init_count", state[m]["count"])
        state[m]["history"].clear()
        
    if target == "all" or (mode == "Global" and not target):
        for m in ["Forge", "Skill", "Pet", "Mount"]: _reset_module(m)
        print("[전체 상태 초기화 완료]")
    else:
        if mode == "Global":
            print("사용법: reset (현재 모듈 초기화) 또는 reset all (전체 초기화)")
            return True
        _reset_module(mode)
        print(f"{UI_COLORS[mode]}[{mode}]{COLOR_RESET} 상태 초기화 완료")
    return True

def handle_status_command(state, mode):
    if mode == "Global":
        print("특정 모듈에 진입해야 상태를 확인할 수 있습니다. (예: mode forge)")
        return True
    s = state[mode]
    asc_lvl = min(4, max(0, s.get('ascension_level', 0)))
    stars = "★" * asc_lvl + "☆" * (4 - asc_lvl)
    
    if mode == "Forge":
        print(f"{UI_COLORS['Forge']}[{mode}]{COLOR_RESET} Level: {s['level']:>2} | Ascension: {stars} | Chance: {s['chance']:>4.1f}% | Seed: {s['seed']:016X}")
    else:
        max_cnt = get_max_count(mode, s['level'])
        print(f"{UI_COLORS[mode]}[{mode}]{COLOR_RESET} Level: {s['level']+1:>2}({s['count']:>3}/{max_cnt:>3}) | Ascension: {stars} | Chance: {s['chance']:>4.1f}% | Seed: {s['seed']:016X}")
    return True

def handle_help_command(mode, args):
    if not args:
        print("\n[ 명령어 리스트 ]")
        if mode == "Global":
            print("  tutorial, help, mode, report, reset, save, load, exit")
        elif mode == "Forge":
            print("  forge, search, report, status, set, reset, return")
        elif mode == "Skill":
            print("  summon, search, report, status, set, reset, return")
        elif mode in ["Pet", "Mount"]:
            print("  summon, search, optimize, report, status, set, reset, return")
        print("\n💡 [help 명령어]를 입력하시면 상세 설명을 보실 수 있습니다!")
        return True

    target = args[0].lower()
    print(f"\n[ '{target}' 상세 설명 ]")
    if target == "tutorial":
        print("형식 : tutorial")
        print("기능 : 프로그램의 전체적인 흐름을 익힐 수 있는 대화형 가이드를 시작합니다.")
        print("예시 : tutorial")
    elif target == "mode":
        print("형식 : mode [모듈명]")
        print("기능 : 지정한 모듈의 시뮬레이터로 진입합니다. (forge, skill, pet, mount)")
        print("예시 : mode forge")
    elif target == "report":
        print("형식 : report <모듈명:all>")
        print("기능 : 현재까지 진행된 통계와 최고 획득 결과를 요약합니다.")
        print("예시 1 : report")
        print("예시 2 : report all")
    elif target == "set":
        print("형식 : set [속성]:[값]")
        print("기능 : 시뮬레이션 환경 변수를 임의로 조작합니다. (level, chance)")
        print("예시 1 : set level:20")
        print("예시 2 : set chance:15.5")
    elif target == "reset":
        print("형식 : reset <모듈명:all>")
        print("기능 : 소환 기록을 지우고, 초기 셋업 상태로 되돌립니다.")
        print("예시 1 : reset")
        print("예시 2 : reset all")
    elif target == "save":
        print("형식 : save [파일이름]")
        print("기능 : 모든 시뮬레이션 상태와 기록을 파일로 저장합니다.")
        print("예시 : save my_data")
    elif target == "load":
        print("형식 : load [파일이름]")
        print("기능 : 저장된 파일을 불러와 시뮬레이션을 이어서 진행합니다.")
        print("예시 : load my_data")
    elif target == "search":
        print("형식 : search <tier:값> <perf:값> <type:값> <stat:스탯명:완성도>")
        print("기능 : 지정한 조건 이상(>=)인 모든 결과를 필터링하여 검색합니다.")
        print("예시 1 : search tier:quantum perf:90")
        print("예시 2 : search stat:criticalchance:95 stat:attackspeed:90")
    elif target in ["forge", "summon"]:
        print(f"형식 : {target} amount:[수량] <times:1>")
        print(f"기능 : 지정한 수량만큼 {'장비를 제작' if target=='forge' else '소환을 진행'}합니다.")
        print(f"예시 1 : {target} amount:100")
        print(f"예시 2 : {target} amount:50 times:10")
    elif target == "optimize":
        print("형식 : optimize amount:[수량] mode:[bonus/stat/shortcut] <tier:신화>")
        print("기능 : DP 알고리즘을 사용하여 정해진 재화 내에서 100% 최적의 소환 경로를 계산합니다.")
        print("모드 설명:")
        print("  - mode:bonus    -> 정해진 재화 내에서 보너스 발생 횟수를 극대화")
        print("  - mode:stat     -> 정해진 재화 내에서 타겟 티어의 비틱 스탯을 스나이핑")
        print("  - mode:shortcut -> 타겟 티어 펫을 목표 수량(amount)만큼 얻기 위한 최소 비용 최단기 경로 탐색")
        print("예시 1 : optimize amount:10000 mode:bonus")
        print("예시 2 : optimize amount:3 mode:shortcut tier:mythic")
    elif target == "status":
        print("형식 : status")
        print("기능 : 현재 레벨, 카운트, 추가 확률, 승천 상태 등을 확인합니다.")
        print("예시 : status")
    elif target == "return":
        print("형식 : return")
        print("기능 : 현재 모듈에서 빠져나와, 기본 모드(Global)로 돌아갑니다.")
        print("예시 : return")
    elif target == "exit":
        print("형식 : exit")
        print("기능 : 시뮬레이터 프로그램을 완전히 종료합니다.")
        print("예시 : exit")
    else:
        print("해당 명령어에 대한 상세 도움말이 없습니다.")
    return True

def execute_command(state, cmd_input):
    parts = cmd_input.split()
    cmd = parts[0].lower()
    args = parts[1:]
    mode = state["current_mode"]

    if state["tutorial_step"] > 0 and cmd in ["quit", "return", "exit"]:
        print("\n[ 🎓 튜토리얼을 종료합니다. ]\n")
        state["tutorial_step"] = 0
        if cmd == "exit": return False
        return True

    if cmd == "exit":
        print("프로그램을 완전히 종료합니다.")
        return False

    is_global = process_global_command(state, cmd, args)
    
    if not is_global:
        if mode != "Global":
            route_module_command(state, mode, cmd, args)
        else:
            print(f"'{cmd}' 명령어를 찾을 수 없습니다. (전체 명령어를 보려면 'help' 입력)")
            
    from utils.tutorial import advance_tutorial
    advance_tutorial(state, cmd, state["current_mode"])
    return True

def process_global_command(state, cmd, args):
    mode = state["current_mode"]

    if cmd == "mode":
        if args and args[0].capitalize() in ["Forge", "Skill", "Pet", "Mount", "Egg"]:
            target = args[0].capitalize()
            state["current_mode"] = "Pet" if target == "Egg" else target
        else: print("사용법: mode [forge/skill/pet/mount]")
        return True
        
    elif cmd == "tutorial":
        import utils.tutorial as tut
        return tut.start_tutorial(state)
        
    elif cmd == "set": return handle_set_command(state, mode, args)
    elif cmd == "reset": return handle_reset_command(state, mode, args)
    elif cmd == "save":
        if args: save_state(state, args[0])
        else: print("사용법: save [파일이름]")
        return True
    elif cmd == "load":
        if args: load_state(state, args[0])
        else: print("사용법: load [파일이름]")
        return True
    elif cmd == "status": return handle_status_command(state, mode)
    
    elif cmd == "report":
        if not args:
            if mode == "Global":
                print("사용법: report <모듈명:all>")
                return True
            return False 
        target = args[0].lower()
        if target == "all":
            print_report_all(state)
            return True
        elif target in ["forge", "skill", "pet", "egg", "mount"]:
            t_mode = "Pet" if target == "egg" else target.capitalize()
            route_module_command(state, t_mode, "report", [])
            return True
        else:
            print("사용법: report <모듈명:all> 또는 report (현재 모드)")
            return True
            
    elif cmd == "help": return handle_help_command(mode, args)
    elif cmd in ["return", "quit"]:
        if mode == "Global": print("이미 기본 모드입니다. 프로그램을 종료하려면 'exit'를 입력하세요.")
        else: state["current_mode"] = "Global"
        return True
    return False

def route_module_command(state, mode, cmd, args):
    try:
        if mode == "Forge":
            import utils.forge as forge_module
            forge_module.handle_command(state, cmd, args)
        elif mode == "Skill":
            import utils.skill as skill_module
            skill_module.handle_command(state, cmd, args)
        elif mode == "Pet":
            import utils.egg as pet_module
            pet_module.handle_command(state, cmd, args)
        elif mode == "Mount":
            import utils.mount as mount_module
            mount_module.handle_command(state, cmd, args)
    except ModuleNotFoundError:
        print(f"[{mode}] 관련 유틸리티 모듈을 찾을 수 없습니다. (utils 폴더 확인)")
    except AttributeError:
        print(f"[{mode}] 모듈에 handle_command 함수가 구현되지 않았습니다.")