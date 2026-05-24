import json
import os
from utils.metaplay_pcg import MetaplayPCG
from utils.constants import (
    COLOR_RESET, AGE_COLOR, AGE_NAME, AGE_KOR_SPACED, TYPE_KOR_SPACED, SUBSTATS_POOL,
    get_gradient_color, get_substat_value, get_padded_kor, parse_kwargs
)

DISPLAY_TYPE_ORDER = ["Helmet", "Armour", "Gloves", "Necklace", "Ring", "Melee Weapon", "Ranged Weapon", "Shoes", "Belt"]
TYPE_JSON_ORDER = ["Helmet", "Armour", "Gloves", "Necklace", "Ring", "Weapon", "Shoes", "Belt"]

TYPE_KOR_MAP = {
    "all": "all", "전체": "all", "모두": "all", 
    "무기": "all_weapons", "weapon": "all_weapons",
    "근거리": "melee_weapons", "melee": "melee_weapons", 
    "원거리": "ranged_weapons", "ranged": "ranged_weapons",
    "투구": "Helmet", "helmet": "Helmet",
    "갑옷": "Armour", "armour": "Armour", "armor": "Armour",
    "장갑": "Gloves", "gloves": "Gloves",
    "신발": "Shoes", "shoes": "Shoes",
    "벨트": "Belt", "belt": "Belt",
    "목걸이": "Necklace", "necklace": "Necklace",
    "반지": "Ring", "ring": "Ring"
}

def format_stat_with_color(ds_list, idx, width=27):
    if not ds_list or len(ds_list) <= idx: return get_padded_kor("-", width)
    ds = ds_list[idx]
    color = get_gradient_color(ds['perf'])
    vis_str = f"{ds['name']} (+{ds['value']:.2f}%)"
    pad = width - len(vis_str)
    left, right = pad // 2, pad - (pad // 2)
    return (" " * left) + f"{ds['name']} ({color}+{ds['value']:.2f}%{COLOR_RESET})" + (" " * right)

def load_forge_data():
    try:
        with open('configs/ItemAgeDropChancesLibrary.json', 'r', encoding='utf-8') as f:
            age_drop = json.load(f)
        with open('configs/ItemBalancingLibrary.json', 'r', encoding='utf-8') as f:
            equip_lib = json.load(f)
        with open('configs/SecondaryStatItemUnlockLibrary.json', 'r', encoding='utf-8') as f:
            stat_unlocks = json.load(f)
            
        weapon_props_map = {}
        try:
            with open('configs/WeaponLibrary.json', 'r', encoding='utf-8') as f:
                weapon_lib = json.load(f)
                for v in weapon_lib.values():
                    w_age, w_idx = v.get("ItemId", {}).get("Age"), v.get("ItemId", {}).get("Idx")
                    w_range, w_windup = v.get("AttackRange", 0), v.get("WindupTime", 0.0)
                    if w_age is not None and w_idx is not None:
                        weapon_props_map[(w_age, w_idx)] = {"is_ranged": (w_range >= 7), "windup": w_windup}
        except FileNotFoundError: pass

        items_by_age_and_type = {i: {} for i in range(10)}
        for key, data in equip_lib.items():
            age, itype, idx = data['ItemId']['Age'], data['ItemId']['Type'], data['ItemId'].get('Idx', 0)
            if itype == "Weapon":
                props = weapon_props_map.get((age, idx), {})
                data["IsRanged"] = props.get("is_ranged", False)
                data["WindupTime"] = props.get("windup", 0.0)
            if age <= 9:
                if itype not in items_by_age_and_type[age]: items_by_age_and_type[age][itype] = []
                items_by_age_and_type[age][itype].append(data)
        return age_drop, items_by_age_and_type, stat_unlocks
    except FileNotFoundError:
        print("에러: configs 폴더에 대장간용 JSON 파일이 없습니다.")
        return None, None, None

def simulate_single_forge(current_seed, forge_level, free_chance_pct, age_drop, items_by_age_and_type, stat_unlocks, is_ascended):
    pcg = MetaplayPCG(current_seed)
    age_roll, acc, rolled_age = pcg.next_f64(), 0.0, 0
    lvl_chances = age_drop.get(str(forge_level), {})
    for age in range(10):
        acc += lvl_chances.get(f"Age{age}", 0.0)
        if age_roll < acc:
            rolled_age = age
            break
            
    available_types = sorted(list(items_by_age_and_type[rolled_age].keys()), key=lambda x: TYPE_JSON_ORDER.index(x) if x in TYPE_JSON_ORDER else 99)
    if not available_types: return None
        
    chosen_type, count = None, 0
    for t in available_types:
        count += 1
        if pcg.next_int(count) == 0: chosen_type = t
            
    pcg.next_guid()
    specific_items = items_by_age_and_type[rolled_age][chosen_type]
    chosen_item_data = specific_items[pcg.next_int(len(specific_items))]
    _ = pcg.next_int(100)
    
    num_subs = stat_unlocks.get(str(rolled_age), {}).get("NumberOfSecondStats", 0)
    if is_ascended:
        num_subs = max(2, num_subs)
        
    avail_stats = list(SUBSTATS_POOL)
    
    display_type, is_ranged, windup_time = chosen_type, False, 0.0
    if chosen_type == "Weapon":
        is_ranged = chosen_item_data.get("IsRanged", False)
        windup_time = chosen_item_data.get("WindupTime", 0.0)
        display_type = "Ranged Weapon" if is_ranged else "Melee Weapon"
        if is_ranged:
            if "Melee Damage" in avail_stats: avail_stats.remove("Melee Damage")
        elif "Ranged Damage" in avail_stats: avail_stats.remove("Ranged Damage")
            
    acquired, detailed_stats, f64_sum, stat_dict = [], [], 0.0, {}
    for _ in range(num_subs):
        if not avail_stats: break
        s_name = avail_stats.pop(pcg.next_int(len(avail_stats)))
        f64_val = pcg.next_f64()
        f64_sum += f64_val
        s_val = get_substat_value(s_name, f64_val)
        detailed_stats.append({"name": s_name, "value": s_val * 100.0, "perf": f64_val * 100.0})
        acquired.append(f"{s_name} (+{s_val*100:.2f}%)")
        stat_dict[s_name] = s_val * 100.0
        
    return {
        "Age": rolled_age, "Type": display_type, "IsRanged": is_ranged, "Windup": windup_time,
        "Stats": acquired, "DetailedStats": detailed_stats, "Perf": (f64_sum / max(1, num_subs)) * 100.0,
        "StatDict": stat_dict, "IsFree": pcg.next_f64() < (free_chance_pct / 100.0), "Seed": current_seed
    }

def get_age_by_string(name):
    name = name.lower().replace(" ", "")
    for k, v in AGE_NAME.items():
        if v.lower() == name or AGE_KOR_SPACED.get(k, "").replace(" ", "") == name: return k
    return -1

def do_forge(state, args, age_drop, items_by_age_and_type, stat_unlocks):
    kwargs, pos = parse_kwargs(args)
    amount_str = kwargs.get('amount') or (pos[0] if len(pos) > 0 else None)
    times_str = kwargs.get('times') or (pos[1] if len(pos) > 1 else '1')
    
    if not amount_str:
        print("사용법: forge amount:[수량] <times:1> (예: forge amount:100)")
        return
    try:
        amount, times = int(amount_str), int(times_str)
        if amount <= 0 or times <= 0: raise ValueError
    except ValueError:
        print("수량과 반복횟수는 양의 정수여야 합니다.")
        return

    f_state = state["Forge"]
    batch_size = amount * times
    current_seed, current_level, extra_chance = f_state["seed"], f_state["level"] - 1, f_state["chance"]
    is_ascended = f_state.get("is_ascended", False)
    
    top = "┌" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*10 + "┬" + "─"*10 + "┬" + "─"*27 + "┬" + "─"*27 + "┬" + "─"*10 + "┬" + "─"*8 + "┐"
    mid = "├" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*10 + "┼" + "─"*10 + "┼" + "─"*27 + "┼" + "─"*27 + "┼" + "─"*10 + "┼" + "─"*8 + "┤"
    bot = "└" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*10 + "┴" + "─"*10 + "┴" + "─"*27 + "┴" + "─"*27 + "┴" + "─"*10 + "┴" + "─"*8 + "┘"
    
    age_counts, free_count = {i: 0 for i in range(10)}, 0
    for _ in range(batch_size):
        res = simulate_single_forge(current_seed, current_level, extra_chance, age_drop, items_by_age_and_type, stat_unlocks, is_ascended)
        if res:
            age_counts[res['Age']] += 1
            if res['IsFree']: free_count += 1
            res['index'] = len(f_state["history"]) + 1
            f_state["history"].append(res)
        current_seed += 1

    f_state["seed"] = current_seed
    age_summary_str = " | ".join(f"{AGE_COLOR.get(a, COLOR_RESET)}{AGE_KOR_SPACED[a].strip()}{COLOR_RESET}: {age_counts[a]}" for a in reversed(range(10)) if age_counts[a] > 0)
    
    print(f"\n[ {amount}회 × {times}번 제작 결과: 총 {batch_size}회 소모 (무료 제작: {free_count}회) | {age_summary_str} ]")
    print(top)
    print("│  순번  │   티어   │   타입   │ 와인드업 │           스탯 1          │           스탯 2          │  완성도  │  무료  │")
    print(mid)
    
    for res in f_state["history"][-batch_size:]:
        colored_age = f"{AGE_COLOR.get(res['Age'], COLOR_RESET)}{get_padded_kor(AGE_KOR_SPACED.get(res['Age']), 8)}{COLOR_RESET}"
        kor_type = get_padded_kor(TYPE_KOR_SPACED.get(res['Type'], res['Type']), 8)
        windup_str = get_padded_kor(f"{res.get('Windup', 0.0):.3f}", 8) if "Weapon" in res['Type'] else get_padded_kor("-", 8)
        
        s1_pad = format_stat_with_color(res['DetailedStats'], 0, 27)
        s2_pad = format_stat_with_color(res['DetailedStats'], 1, 27)
        perf_str = f"{get_gradient_color(res['Perf'])}{res['Perf']:>6.2f}%{COLOR_RESET}"
        bonus_str = "   🍀   " if res['IsFree'] else "        "
        
        print(f"│ {res['index']:>6} │ {colored_age} │ {kor_type} │ {windup_str} │{s1_pad}│{s2_pad}│ {perf_str}  │{bonus_str}│")
    print(bot)

def do_summary(state):
    history = state["Forge"]["history"]
    if not history: return print("제작 기록이 없습니다.")

    free_cnt, total_pulls = sum(1 for p in history if p['IsFree']), len(history)
    print(f"\n- 대장간 레벨: {state['Forge']['level']}\n- 소모한 망치: {total_pulls - free_cnt}\n-   제작 횟수: {total_pulls}\n-   무료 제작: {free_cnt}\n" + "─"*119 + "\n" + " "*50 + "[ 티어별 획득 수 ]")
    
    counts = {i: {"base": 0, "bonus": 0} for i in range(10)}
    for p in history: counts[p['Age']]["bonus" if p['IsFree'] else "base"] += 1
    for a in reversed(range(10)):
        if (tot := counts[a]["base"] + counts[a]["bonus"]) > 0:
            print(f"- {AGE_COLOR.get(a, COLOR_RESET)}{get_padded_kor(AGE_KOR_SPACED[a], 8)}{COLOR_RESET}: {tot:>6}")
    
    best_age = max(history, key=lambda x: x['Age'])['Age']
    best_by_type = {}
    for item in [x for x in history if x['Age'] == best_age]:
        if item['Type'] not in best_by_type or item['Perf'] > best_by_type[item['Type']]['Perf']: best_by_type[item['Type']] = item

    print("─"*119 + f"\n\n {AGE_COLOR.get(best_age, COLOR_RESET)}[{get_padded_kor(AGE_KOR_SPACED[best_age], 8).strip()}]{COLOR_RESET} 타입별 최고 스탯 정보 ")
    print("┌" + "─"*10 + "┬" + "─"*10 + "┬" + "─"*27 + "┬" + "─"*27 + "┬" + "─"*10 + "┐\n│   타입   │ 와인드업 │           스탯 1          │           스탯 2          │  완성도  │\n├" + "─"*10 + "┼" + "─"*10 + "┼" + "─"*27 + "┼" + "─"*27 + "┼" + "─"*10 + "┤")
    
    for t in DISPLAY_TYPE_ORDER:
        if res := best_by_type.get(t):
            kor_type = get_padded_kor(TYPE_KOR_SPACED.get(res['Type'], res['Type']), 8)
            windup_str = get_padded_kor(f"{res.get('Windup', 0.0):.3f}", 8) if "Weapon" in res['Type'] else get_padded_kor("-", 8)
            s1_pad = format_stat_with_color(res['DetailedStats'], 0, 27)
            s2_pad = format_stat_with_color(res['DetailedStats'], 1, 27)
            perf_str = f"{get_gradient_color(res['Perf'])}{res['Perf']:>6.2f}%{COLOR_RESET}"
            
            print(f"│ {kor_type} │ {windup_str} │{s1_pad}│{s2_pad}│ {perf_str}  │")
    print("└" + "─"*10 + "┴" + "─"*10 + "┴" + "─"*27 + "┴" + "─"*27 + "┴" + "─"*10 + "┘")

def do_search(state, args):
    target_name, target_perf, target_type_raw = None, 0.0, "all"
    target_stats = {} # {"health": 90.0, "criticalchance": 0.0}
    
    pos_idx = 0
    for arg in args:
        lower_arg = arg.lower()
        if lower_arg.startswith("tier:"): target_name = arg.split(":", 1)[1]
        elif lower_arg.startswith("perf:"):
            try: target_perf = float(arg.split(":", 1)[1])
            except ValueError: return print("완성도(perf)는 숫자로 입력하세요.")
        elif lower_arg.startswith("type:"): target_type_raw = arg.split(":", 1)[1]
        elif lower_arg.startswith("stat:"):
            parts = arg.split(":")
            if len(parts) >= 2:
                s_name = parts[1].lower().replace("_", "").replace(" ", "")
                s_perf = 0.0
                if len(parts) >= 3:
                    try: s_perf = float(parts[2])
                    except ValueError: return print("스탯 완성도(stat:스탯명:숫자)는 숫자로 입력하세요.")
                target_stats[s_name] = s_perf
        elif ":" not in arg:
            if pos_idx == 0 and not target_name: target_name = arg
            elif pos_idx == 1:
                try: target_perf = float(arg)
                except ValueError: pass
            elif pos_idx == 2: target_type_raw = arg
            pos_idx += 1

    if not target_name: target_name = "원시"

    target_age = get_age_by_string(target_name)
    if target_age == -1: return print(f"'{target_name}' 티어를 찾을 수 없습니다.")
        
    mapped_type = TYPE_KOR_MAP.get(target_type_raw.lower())
    if not mapped_type: return print(f"'{target_type_raw}' 타입을 찾을 수 없습니다.")

    filtered = []
    for res in state["Forge"]["history"]:
        if res['Age'] < target_age: continue
        if res['Perf'] < target_perf: continue
        
        if mapped_type != "all":
            if mapped_type == "all_weapons" and "Weapon" not in res['Type']: continue
            elif mapped_type == "melee_weapons" and res['Type'] != "Melee Weapon": continue
            elif mapped_type == "ranged_weapons" and res['Type'] != "Ranged Weapon": continue
            elif mapped_type not in ["all_weapons", "melee_weapons", "ranged_weapons"] and res['Type'] != mapped_type: continue

        # 아이템의 세부 스탯 파싱
        item_stats = {ds['name'].lower().replace(' ', ''): ds['perf'] for ds in res['DetailedStats']}
        
        # [수정] 타겟 스탯들(AND 조건)이 모두 붙어있고, 각 스탯 완성도 조건을 만족하는지 철저하게 검사
        is_valid = True
        for ts_name, ts_perf in target_stats.items():
            if ts_name not in item_stats:
                is_valid = False
                break
            if item_stats[ts_name] < ts_perf:
                is_valid = False
                break
                
        if not is_valid: continue
        filtered.append(res)
        
    if not filtered: return print(f"조건에 맞는 장비가 없습니다.")
    filtered.sort(key=lambda x: x['Perf'], reverse=True)
    
    colored_title = f"{AGE_COLOR.get(target_age, COLOR_RESET)}{AGE_KOR_SPACED[target_age].strip()}({AGE_NAME[target_age]}){COLOR_RESET}"
    
    print(f"\n[ {colored_title} 이상 장비 검색 결과 (조건 충족) ]\n┌" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*10 + "┬" + "─"*10 + "┬" + "─"*27 + "┬" + "─"*27 + "┬" + "─"*10 + "┐\n│  순번  │   티어   │   타입   │ 와인드업 │           스탯 1          │           스탯 2          │  완성도  │\n├" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*10 + "┼" + "─"*10 + "┼" + "─"*27 + "┼" + "─"*27 + "┼" + "─"*10 + "┤")
    
    for res in filtered:
        colored_age = f"{AGE_COLOR.get(res['Age'], COLOR_RESET)}{get_padded_kor(AGE_KOR_SPACED.get(res['Age']), 8)}{COLOR_RESET}"
        kor_type = get_padded_kor(TYPE_KOR_SPACED.get(res['Type'], res['Type']), 8)
        windup_str = get_padded_kor(f"{res.get('Windup', 0.0):.3f}", 8) if "Weapon" in res['Type'] else get_padded_kor("-", 8)
        s1_pad = format_stat_with_color(res['DetailedStats'], 0, 27)
        s2_pad = format_stat_with_color(res['DetailedStats'], 1, 27)
        perf_str = f"{get_gradient_color(res['Perf'])}{res['Perf']:>6.2f}%{COLOR_RESET}"
        
        print(f"│ {res['index']:>6} │ {colored_age} │ {kor_type} │ {windup_str} │{s1_pad}│{s2_pad}│ {perf_str}  │")
    print("└" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*10 + "┴" + "─"*10 + "┴" + "─"*27 + "┴" + "─"*27 + "┴" + "─"*10 + "┘")

def handle_command(state, cmd, args):
    data = load_forge_data()
    if data == (None, None, None): return
    if cmd in ["forge", "summon"]: do_forge(state, args, data[0], data[1], data[2])
    elif cmd == "summary": do_summary(state)
    elif cmd == "search": do_search(state, args)
    else: print(f"[Forge] 지원하지 않는 명령어입니다: {cmd}")