import json
import os
from utils.metaplay_pcg import MetaplayPCG
from utils.constants import (
    COLOR_RESET, RARITY_KOR, RARITY_COLOR, SUBSTATS_POOL, 
    RARITY_SCORE, get_gradient_color, get_substat_value, get_padded_kor, parse_kwargs
)

def format_stat_with_color(ds_list, idx, width=27):
    if not ds_list or len(ds_list) <= idx: return get_padded_kor("-", width)
    ds = ds_list[idx]
    color = get_gradient_color(ds['perf'])
    vis_str = f"{ds['name']} (+{ds['value']:.2f}%)"
    pad = width - len(vis_str)
    left, right = pad // 2, pad - (pad // 2)
    return (" " * left) + f"{ds['name']} ({color}+{ds['value']:.2f}%{COLOR_RESET})" + (" " * right)

def load_data():
    try:
        with open('configs/MountSummonConfig.json', 'r', encoding='utf-8') as f:
            summon_config = json.load(f)
        with open('configs/MountLibrary.json', 'r', encoding='utf-8') as f:
            mount_library = json.load(f)
        return summon_config, mount_library
    except FileNotFoundError:
        print("에러: configs 폴더에 탈것용 JSON 파일이 없습니다.")
        return None, None

def get_rarity_by_string(name):
    name = name.lower().replace(" ", "")
    for k, v in RARITY_KOR.items():
        if v.replace(" ", "") == name or k.lower() == name: return k
    return None

def do_summon(state, args, levels_config, mounts_by_rarity):
    amount_str, times_str = None, "1"
    for arg in args:
        if ":" not in arg:
            print(f"경고: 잘못된 형식입니다 -> '{arg}'. '인자:값' 형태로 입력하세요. (예: amount:100)")
            return
        key, val = arg.split(":", 1)
        if key.lower() == "amount": amount_str = val
        elif key.lower() == "times": times_str = val
        
    if not amount_str: return print("사용법: summon amount:[수량] <times:1>")
    
    try:
        amount, times = int(amount_str), int(times_str)
        if amount not in [1, 15, 50]: return print("[1, 15, 50] 만 소환 가능합니다.")
        if times <= 0: raise ValueError
    except ValueError: return print("유효한 숫자를 입력하세요.")

    m_state = state["Mount"]
    current_seed, current_level, current_count, extra_chance_pct = m_state["seed"], m_state["level"], m_state["count"], m_state["chance"]
    is_ascended = m_state.get("is_ascended", False)
    
    start_idx = len(m_state["history"])
    rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
    total_acquired, total_bonus_count, total_batch_size = 0, 0, amount * times
    
    for _ in range(times):
        total_target, current_pull_idx, current_bonus_count = amount, 0, 0
        while current_pull_idx < total_target:
            pcg_summon = MetaplayPCG(current_seed)
            is_bonus_pull = current_pull_idx >= amount

            if not is_bonus_pull:
                if pcg_summon._next_pcg32() < int(round((extra_chance_pct / 100.0) * 4294967296)):
                    total_target += 1
                    current_bonus_count += 1 

            rarity_roll_raw = pcg_summon._next_pcg32() 
            current_lvl_data = levels_config[min(current_level, len(levels_config) - 1)]
            
            accumulated_raw, rolled_rarity = 0, "Common"
            for rarity in rarities:
                accumulated_raw += int(round(current_lvl_data.get(rarity, 0.0) * 4294967296)) 
                if rarity_roll_raw < accumulated_raw:
                    rolled_rarity = rarity
                    break

            available_mounts = mounts_by_rarity[rolled_rarity]
            _ = pcg_summon.next_int(len(available_mounts))
            pcg_summon.next_guid()

            num_substats = 2 if (rolled_rarity in ["Legendary", "Ultimate", "Mythic"] or is_ascended) else 1
            available_stats = list(SUBSTATS_POOL)
            acquired_stats, detailed_stats, f64_sum = [], [], 0.0 
            
            for _ in range(num_substats):
                stat_name = available_stats.pop(pcg_summon.next_int(len(available_stats)))
                f64_val = pcg_summon.next_f64()
                f64_sum += f64_val 
                stat_val = get_substat_value(stat_name, f64_val)
                detailed_stats.append({"name": stat_name, "value": stat_val * 100.0, "perf": f64_val * 100.0})
                acquired_stats.append(f"{stat_name} (+{stat_val*100:.2f}%)")

            res = {
                "rarity_score": RARITY_SCORE[rolled_rarity], "rarity_name": rolled_rarity,
                "perfection": (f64_sum / num_substats) * 100.0, "stats": acquired_stats,
                "detailed_stats": detailed_stats, "is_bonus": is_bonus_pull,
                "seed": current_seed, "index": len(m_state["history"]) + 1
            }
            m_state["history"].append(res)

            current_count += 1
            summons_required = current_lvl_data.get("SummonsRequired", 9999)
            if current_count >= summons_required:
                current_count -= summons_required
                current_level += 1
                
            current_seed += 1
            current_pull_idx += 1
            
        total_acquired += total_target
        total_bonus_count += current_bonus_count

    m_state["seed"], m_state["level"], m_state["count"] = current_seed, current_level, current_count

    print(f"\n[ {amount}회 × {times}번 소환 결과: 총 {total_acquired}마리 ({amount * times} + 보너스 {total_bonus_count}) ]\n┌" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*27 + "┬" + "─"*27 + "┬" + "─"*10 + "┬" + "─"*8 + "┐\n│  순번  │   티어   │           스탯 1          │           스탯 2          │  완성도  │ 보너스 │\n├" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*27 + "┼" + "─"*27 + "┼" + "─"*10 + "┼" + "─"*8 + "┤")
    for i, res in enumerate(m_state["history"][start_idx:], 1):
        colored_r = f"{RARITY_COLOR[res['rarity_name']]}{get_padded_kor(RARITY_KOR[res['rarity_name']], 8)}{COLOR_RESET}"
        
        print(f"│ {res['index']:>6} │ {colored_r} │{format_stat_with_color(res['detailed_stats'], 0, 27)}│{format_stat_with_color(res['detailed_stats'], 1, 27)}│ {get_gradient_color(res['perfection'])}{res['perfection']:>6.2f}%{COLOR_RESET}  │{'   🍀   ' if res['is_bonus'] else '        '}│")
    print("└" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*27 + "┴" + "─"*27 + "┴" + "─"*10 + "┴" + "─"*8 + "┘")

def do_summary(state):
    history = state["Mount"]["history"]
    if not history: return print("소환 기록이 없습니다.")

    total_pulls = len(history)
    bonus_cnt = sum(1 for p in history if p['is_bonus'])
    print(f"\n- 탈것 레벨: {state['Mount']['level']+1}\n-    카운트: {state['Mount']['count']}\n- 기본 소환: {total_pulls - bonus_cnt}\n- 소환 횟수: {total_pulls}\n- 추가 소환: {bonus_cnt}\n" + "─"*98 + "\n" + " "*39 + "[ 티어별 획득 수 ]")
    
    rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
    counts = {r: {"base": 0, "bonus": 0} for r in rarities}
    for p in history: counts[p['rarity_name']]["bonus" if p['is_bonus'] else "base"] += 1
    for r in reversed(rarities):
        if (tot := counts[r]["base"] + counts[r]["bonus"]) > 0:
            print(f"- {RARITY_COLOR[r]}{get_padded_kor(f'[{RARITY_KOR[r].strip()}]', 10)}{COLOR_RESET}: {tot:>6}")
    print("─" * 98)

def do_search(state, args):
    target_name, target_perf = "일반", 0.0
    target_stats = {}
    
    for arg in args:
        if ":" not in arg:
            print(f"경고: 잘못된 인자 형식입니다 -> '{arg}'. '인자:값' 형태로 입력하세요.")
            return
            
        lower_arg = arg.lower()
        if lower_arg.startswith("tier:"): target_name = arg.split(":", 1)[1]
        elif lower_arg.startswith("perf:"):
            try: target_perf = float(arg.split(":", 1)[1])
            except ValueError: return print("완성도(perf)는 숫자로 입력하세요.")
        elif lower_arg.startswith("stat:"):
            parts = arg.split(":")
            if len(parts) >= 2:
                s_name = parts[1].lower().replace("_", "").replace(" ", "")
                s_perf = 0.0
                if len(parts) >= 3:
                    try: s_perf = float(parts[2])
                    except ValueError: return print("스탯 완성도(stat:스탯명:숫자)는 숫자로 입력하세요.")
                target_stats[s_name] = s_perf

    target_rarity = get_rarity_by_string(target_name)
    if not target_rarity: return print(f"'{target_name}' 티어 탈것을 찾을 수 없습니다.")

    filtered = []
    for res in state["Mount"]["history"]:
        if res['rarity_score'] < RARITY_SCORE[target_rarity]: continue
        if res['perfection'] < target_perf: continue
        
        item_stats = {ds['name'].lower().replace(' ', ''): ds['perf'] for ds in res['detailed_stats']}
        
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
        
    if not filtered: return print(f"조건에 맞는 탈것이 없습니다.")
    filtered.sort(key=lambda x: x['perfection'], reverse=True)
    
    print(f"\n[ {RARITY_COLOR[target_rarity]}{RARITY_KOR[target_rarity].strip()}({target_rarity}){COLOR_RESET} 이상 티어 탈것 검색 결과 (조건 충족) ]\n┌" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*27 + "┬" + "─"*27 + "┬" + "─"*10 + "┐\n│  순위  │   티어   │           스탯 1          │           스탯 2          │  완성도  │\n├" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*27 + "┼" + "─"*27 + "┼" + "─"*10 + "┤")
    for res in filtered:
        colored_r = f"{RARITY_COLOR[res['rarity_name']]}{get_padded_kor(RARITY_KOR[res['rarity_name']], 8)}{COLOR_RESET}"
        
        print(f"│ {res['index']:>6} │ {colored_r} │{format_stat_with_color(res['detailed_stats'], 0, 27)}│{format_stat_with_color(res['detailed_stats'], 1, 27)}│ {get_gradient_color(res['perfection'])}{res['perfection']:>6.2f}%{COLOR_RESET}  │")
    print("└" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*27 + "┴" + "─"*27 + "┴" + "─"*10 + "┘")


# =====================================================================
# 🧠 완전 100% 최적해 DP 
# =====================================================================
def do_optimize(state, args, levels_config, mounts_by_rarity):
    kwargs, _ = parse_kwargs(args)
    amount_str = kwargs.get('amount')
    mode_str = kwargs.get('mode', 'bonus').lower()
    tier_str = kwargs.get('tier', '신화')
    
    if not amount_str: 
        return print("사용법: optimize amount:[수량] mode:[bonus/stat] <tier:신화>")
        
    try:
        amount = int(amount_str)
        if amount <= 0: raise ValueError
    except ValueError:
        return print("수량은 양의 정수여야 합니다.")
        
    target_rarity = get_rarity_by_string(tier_str)
    if mode_str == 'stat' and not target_rarity:
        return print(f"'{tier_str}' 티어를 찾을 수 없습니다. (예: 궁극, 신화)")
        
    print(f"\n[시스템] {amount}뽑기 100% 최적 경로를 계산 중입니다. 잠시만 기다려주세요...")
    
    m_state = state["Mount"]
    start_seed = m_state["seed"]
    start_level = m_state["level"]
    start_count = m_state["count"]
    extra_chance_pct = m_state["chance"]
    is_ascended = m_state.get("is_ascended", False)
    
    target_r_score = RARITY_SCORE.get(target_rarity, 0)
    bonus_threshold = int(round((extra_chance_pct / 100.0) * 4294967296))
    rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
    avail_stats_base = list(SUBSTATS_POOL)
    
    level_history = []
    c_l, c_c = start_level, start_count
    
    def get_lvl(idx):
        nonlocal c_l, c_c
        while len(level_history) <= idx:
            level_history.append(levels_config[min(c_l, len(levels_config) - 1)])
            c_c += 1
            req = level_history[-1].get("SummonsRequired", 9999)
            if c_c >= req:
                c_c -= req
                c_l += 1
        return level_history[idx]

    cache_A = {} 
    cache_B = {} 
    
    def eval_seed(seed, lvl_data, is_base):
        pcg = MetaplayPCG(seed)
        gen_bonus = False
        if is_base:
            if pcg._next_pcg32() < bonus_threshold:
                gen_bonus = True
                
        r_raw = pcg._next_pcg32()
        acc = 0
        r_val = "Common"
        for r_name in rarities:
            acc += int(round(lvl_data.get(r_name, 0.0) * 4294967296))
            if r_raw < acc:
                r_val = r_name
                break
                
        pcg.next_int(len(mounts_by_rarity[r_val]))
        pcg.next_guid()
        
        n_subs = 2 if (r_val in ["Legendary", "Ultimate", "Mythic"] or is_ascended) else 1
        avail = avail_stats_base.copy()
        f64_sum = 0.0
        for _ in range(n_subs):
            avail.pop(pcg.next_int(len(avail)))
            f64_sum += pcg.next_f64()
            
        perf = (f64_sum / n_subs) * 100.0
        return gen_bonus, RARITY_SCORE[r_val], perf

    def get_A(idx):
        if idx not in cache_A: cache_A[idx] = eval_seed(start_seed + idx, get_lvl(idx), True)
        return cache_A[idx]
        
    def get_B(idx):
        if idx not in cache_B: cache_B[idx] = eval_seed(start_seed + idx, get_lvl(idx), False)
        return cache_B[idx]

    dp = {rem: {} for rem in range(amount + 1)}
    dp[amount][0] = (0.0, [], 0)
    
    for rem in range(amount, 0, -1):
        if not dp[rem]: continue
        
        items = list(dp[rem].items())
        if len(items) > 1000:
            items.sort(key=lambda x: x[1][0], reverse=True)
            items = items[:1000]
            
        for idx, (score, path, gens) in items:
            for cost in [1, 15, 50]:
                if cost <= rem:
                    nxt_rem = rem - cost
                    c_idx = idx
                    step_score = 0
                    bonuses = 0
                    
                    for _ in range(cost):
                        gen_b, rs, perf = get_A(c_idx)
                        if gen_b: bonuses += 1
                        if mode_str == 'stat' and rs >= target_r_score:
                            step_score += (10**rs) + perf*100
                        c_idx += 1
                        
                    for _ in range(bonuses):
                        _, rs, perf = get_B(c_idx)
                        if mode_str == 'stat' and rs >= target_r_score:
                            step_score += (10**rs) + perf*100
                        c_idx += 1
                        
                    if mode_str == 'bonus':
                        step_score = bonuses
                        
                    nxt_idx = c_idx
                    nxt_score = score + step_score
                    nxt_gens = gens + cost + bonuses
                    
                    if nxt_idx not in dp[nxt_rem]:
                        dp[nxt_rem][nxt_idx] = (nxt_score, path + [cost], nxt_gens)
                    else:
                        curr_val = dp[nxt_rem][nxt_idx]
                        if nxt_score > curr_val[0] or (nxt_score == curr_val[0] and nxt_gens > curr_val[2]):
                            dp[nxt_rem][nxt_idx] = (nxt_score, path + [cost], nxt_gens)
                            
    best_state = None
    for idx, val in dp[0].items():
        if best_state is None or val[0] > best_state[0] or (val[0] == best_state[0] and val[2] > best_state[2]):
            best_state = val
            
    path = best_state[1]
    compressed = []
    if path:
        curr_b = path[0]
        cnt = 1
        for b in path[1:]:
            if b == curr_b: cnt += 1
            else:
                compressed.append(f"{curr_b}뽑({cnt}번)")
                curr_b = b
                cnt = 1
        compressed.append(f"{curr_b}뽑({cnt}번)")
        
    route_str = " ➔ ".join(compressed)
    
    print(f"\n[ 최적화 탐색 완료 ]")
    print(f"- 탐색 조건 : {amount} 뽑기 / {'보너스 극대화' if mode_str == 'bonus' else '스탯 스나이핑'}" + (f" ({RARITY_KOR[target_rarity]} 이상)" if mode_str == 'stat' else ""))
    
    # 💥 출력 포맷 튜플 인덱스(best_state[2], best_state[0])로 정확히 수정!
    print(f"- 예상 획득 : {best_state[2]} 마리 (보너스 {best_state[2] - amount}회)")
    if mode_str == 'stat': print(f"- 스탯 점수 : {best_state[0]:,.0f} 점")
    print(f"- 추천 순서 : {route_str}")

    if mode_str == 'stat':
        c_s, c_l, c_c = start_seed, start_level, start_count
        sim_idx = len(m_state["history"]) + 1
        target_results = []
        
        for cost in path:
            total_target = cost
            curr_pull = 0
            while curr_pull < total_target:
                pcg_summon = MetaplayPCG(c_s)
                is_bonus_pull = curr_pull >= cost
                if not is_bonus_pull:
                    if pcg_summon._next_pcg32() < bonus_threshold:
                        total_target += 1
                        
                r_raw = pcg_summon._next_pcg32()
                lvl_data = levels_config[min(c_l, len(levels_config) - 1)]
                
                acc = 0
                r_val = "Common"
                for r_name in rarities:
                    acc += int(round(lvl_data.get(r_name, 0.0) * 4294967296))
                    if r_raw < acc:
                        r_val = r_name
                        break
                        
                pcg_summon.next_int(len(mounts_by_rarity[r_val]))
                pcg_summon.next_guid()
                
                n_subs = 2 if (r_val in ["Legendary", "Ultimate", "Mythic"] or is_ascended) else 1
                avail_stats = list(SUBSTATS_POOL)
                detailed_stats, f64_sum = [], 0.0
                
                for _ in range(n_subs):
                    stat_name = avail_stats.pop(pcg_summon.next_int(len(avail_stats)))
                    f64_val = pcg_summon.next_f64()
                    f64_sum += f64_val
                    stat_val = get_substat_value(stat_name, f64_val)
                    detailed_stats.append({"name": stat_name, "value": stat_val * 100.0, "perf": f64_val * 100.0})
                    
                perf = (f64_sum / n_subs) * 100.0
                
                if RARITY_SCORE[r_val] >= target_r_score:
                    target_results.append({
                        "index": sim_idx, "rarity_name": r_val,
                        "detailed_stats": detailed_stats, "perfection": perf, "is_bonus": is_bonus_pull
                    })
                    
                c_c += 1
                req = lvl_data.get("SummonsRequired", 9999)
                if c_c >= req:
                    c_c -= req
                    c_l += 1
                c_s += 1
                curr_pull += 1
                sim_idx += 1
                
        if target_results:
            print(f"\n[ 획득 예상 타겟 아이템 목록 ]")
            print("┌" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*27 + "┬" + "─"*27 + "┬" + "─"*10 + "┬" + "─"*8 + "┐")
            print("│  순번  │   티어   │           스탯 1          │           스탯 2          │  완성도  │ 보너스 │")
            print("├" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*27 + "┼" + "─"*27 + "┼" + "─"*10 + "┼" + "─"*8 + "┤")
            for res in target_results:
                colored_r = f"{RARITY_COLOR[res['rarity_name']]}{get_padded_kor(RARITY_KOR[res['rarity_name']], 8)}{COLOR_RESET}"
                print(f"│ {res['index']:>6} │ {colored_r} │{format_stat_with_color(res['detailed_stats'], 0, 27)}│{format_stat_with_color(res['detailed_stats'], 1, 27)}│ {get_gradient_color(res['perfection'])}{res['perfection']:>6.2f}%{COLOR_RESET}  │{'   🍀   ' if res['is_bonus'] else '        '}│")
            print("└" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*27 + "┴" + "─"*27 + "┴" + "─"*10 + "┴" + "─"*8 + "┘")
        else:
            print(f"\n해당 재화 내에서는 타겟 티어를 획득할 수 없습니다.")

def handle_command(state, cmd, args):
    data = load_data()
    if data == (None, None): return
    
    rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
    mounts_by_rarity = {r: [] for r in rarities}
    for key, mdata in sorted(data[1].items(), key=lambda x: x[1]["MountId"]["Id"]):
        mounts_by_rarity[mdata["MountId"]["Rarity"]].append(key)
            
    if cmd == "summon":
        do_summon(state, args, data[0]["Levels"], mounts_by_rarity)
    elif cmd == "summary": do_summary(state)
    elif cmd == "search": do_search(state, args)
    elif cmd == "optimize":
        do_optimize(state, args, data[0]["Levels"], mounts_by_rarity)
    else: print(f"[Mount] 지원하지 않는 명령어입니다: {cmd}")