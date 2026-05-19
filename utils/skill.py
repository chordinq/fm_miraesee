import json
import os
from utils.metaplay_pcg import MetaplayPCG
from utils.constants import COLOR_RESET, RARITY_KOR, RARITY_COLOR, RARITY_SCORE, get_padded_kor, parse_kwargs

def load_data():
    try:
        with open('configs/SkillSummonConfig.json', 'r', encoding='utf-8') as f:
            summon_config = json.load(f)
        with open('configs/SkillLibrary.json', 'r', encoding='utf-8') as f:
            skill_library = json.load(f)
        return summon_config, skill_library
    except FileNotFoundError:
        print("에러: configs 폴더에 스킬용 JSON 파일이 없습니다.")
        return None, None

def get_rarity_by_string(name):
    name = name.lower().replace(" ", "")
    for k, v in RARITY_KOR.items():
        if v.replace(" ", "") == name or k.lower() == name: return k
    return None

def do_summon(state, args, levels_config, skills_by_rarity):
    kwargs, pos = parse_kwargs(args)
    amount_str = kwargs.get('amount') or (pos[0] if len(pos) > 0 else None)
    times_str = kwargs.get('times') or (pos[1] if len(pos) > 1 else '1')
    
    if not amount_str: return print("사용법: summon amount:[수량] <times:1>")
    
    try:
        amount, times = int(amount_str), int(times_str)
        if amount not in [5, 75, 250]: return print("[5, 75, 250] 만 소환 가능합니다.")
        if times <= 0: raise ValueError
    except ValueError: return print("유효한 숫자를 입력하세요.")

    s_state = state["Skill"]
    current_seed, current_level, current_count = s_state["seed"], s_state["level"], s_state["count"]
    batch_size = amount * times
    rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
    start_idx = len(s_state["history"])

    for _ in range(batch_size):
        pcg_summon = MetaplayPCG(current_seed)
        pcg_summon._next_pcg32()

        rarity_roll_raw = pcg_summon._next_pcg32() 
        current_lvl_data = levels_config[min(current_level, len(levels_config) - 1)]
        
        accumulated_raw, rolled_rarity = 0, "Common"
        for rarity in rarities:
            accumulated_raw += int(round(current_lvl_data.get(rarity, 0.0) * 4294967296)) 
            if rarity_roll_raw < accumulated_raw:
                rolled_rarity = rarity
                break

        chosen_skill = pcg_summon.choice(skills_by_rarity[rolled_rarity])
        res = {
            "rarity_score": RARITY_SCORE[rolled_rarity], "rarity_name": rolled_rarity,
            "skill_name": chosen_skill, "seed": current_seed, "index": len(s_state["history"]) + 1
        }
        s_state["history"].append(res)

        current_count += 1
        summons_required = current_lvl_data.get("SummonsRequired", 9999)
        if current_count >= summons_required:
            current_count -= summons_required
            current_level += 1
            
        current_seed += 1

    s_state["seed"], s_state["level"], s_state["count"] = current_seed, current_level, current_count

    print(f"\n[ {amount}회 × {times}번 소환 결과: 총 {batch_size}회 소모 ]\n┌" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*27 + "┐\n│  순번  │   티어   │         스킬 이름         │\n├" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*27 + "┤")
    for res in s_state["history"][start_idx:]:
        colored_r = f"{RARITY_COLOR[res['rarity_name']]}{get_padded_kor(RARITY_KOR[res['rarity_name']], 8)}{COLOR_RESET}"
        print(f"│ {res['index']:>6} │ {colored_r} │{res['skill_name']:^27}│")
    print("└" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*27 + "┘")

def do_summary(state):
    history = state["Skill"]["history"]
    if not history: return print("소환 기록이 없습니다.")
    print(f"\n- 스킬 레벨: {state['Skill']['level']+1}\n-    카운트: {state['Skill']['count']}\n- 소환 횟수: {len(history)}\n" + "─"*49 + "\n" + " "*16 + "[ 티어별 획득 수 ]")
    
    rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
    counts = {r: 0 for r in rarities}
    for p in history: counts[p['rarity_name']] += 1
    for r in reversed(rarities):
        if counts[r] > 0:
            print(f"- {RARITY_COLOR[r]}{get_padded_kor(f'[{RARITY_KOR[r].strip()}]', 10)}{COLOR_RESET}: {counts[r]:>6}")
    print("─" * 49)

def do_search(state, args):
    kwargs, pos = parse_kwargs(args)
    target_name = kwargs.get('tier') or (pos[0] if len(pos) > 0 else None)
    
    if not target_name and not kwargs: return print("사용법: search <tier:일반>")
    if not target_name: target_name = "일반"
        
    target_rarity = get_rarity_by_string(target_name)
    if not target_rarity: return print(f"'{target_name}' 티어를 찾을 수 없습니다.")

    filtered = [x for x in state["Skill"]["history"] if x['rarity_score'] >= RARITY_SCORE[target_rarity]]
    if not filtered: return print(f"현재 기록에 조건에 맞는 스킬이 없습니다.")
        
    skill_counts = {}
    for item in filtered: skill_counts[item["skill_name"]] = skill_counts.get(item["skill_name"], 0) + 1
        
    colored_title = f"{RARITY_COLOR[target_rarity]}{RARITY_KOR[target_rarity].strip()}({target_rarity}){COLOR_RESET}"
    print(f"\n[ {colored_title} 이상 티어 스킬 검색 결과 ]\n┌" + "─"*10 + "┬" + "─"*27 + "┬" + "─"*9 + "┐\n│   티어   │         스킬 이름         │ 획득 수 │\n├" + "─"*10 + "┼" + "─"*27 + "┼" + "─"*9 + "┤")
    for s_name, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
        r_name = next(x['rarity_name'] for x in filtered if x['skill_name'] == s_name)
        print(f"│ {RARITY_COLOR[r_name]}{get_padded_kor(RARITY_KOR[r_name], 8)}{COLOR_RESET} │{s_name:^27}│ {count:>4}개  │")
    print("└" + "─"*10 + "┴" + "─"*27 + "┴" + "─"*9 + "┘")

def handle_command(state, cmd, args):
    data = load_data()
    if data == (None, None): return
    if cmd == "summon":
        rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
        skills_by_rarity = {r: [] for r in rarities}
        for key, sdata in data[1].items(): skills_by_rarity[sdata["Rarity"]].append(key)
        do_summon(state, args, data[0]["Levels"], skills_by_rarity)
    elif cmd == "summary": do_summary(state)
    elif cmd == "search": do_search(state, args)
    else: print(f"[Skill] 지원하지 않는 명령어입니다: {cmd}")