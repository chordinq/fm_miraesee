import streamlit as st
import json
import pandas as pd
from metaplay_pcg import MetaplayPCG
from constants import SUBSTATS_POOL, get_substat_value, RARITY_SCORE, RARITY_KOR

WEB_RARITY_COLOR = {
    "Common": "#FFFFFF",      
    "Rare": "#5DD8FF",        
    "Epic": "#5DFF8A",        
    "Legendary": "#FCFF5D",   
    "Ultimate": "#FF5D5D",    
    "Mythic": "#D55DFF"       
}

st.set_page_config(page_title="Forge Master 시뮬레이터", layout="wide")

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif !important;
}

[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #E2E2E2 !important; 
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    font-weight: 500 !important;
    color: #999999 !important;
}

.stButton>button[kind="primary"] {
    height: 55px;
    font-size: 1.4rem;
    font-weight: 800;
    border-radius: 12px;
    background: linear-gradient(180deg, #3498db 0%, #2980b9 100%);
    color: white;
    border: 2px solid #1f618d;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    transition: all 0.1s ease;
}
.stButton>button[kind="primary"]:hover {
    background: linear-gradient(180deg, #5dade2 0%, #3498db 100%);
    border-color: #2980b9;
}
.stButton>button[kind="primary"]:active {
    transform: translateY(2px);
    box-shadow: 0 1px 3px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(mode):
    try:
        if mode == "Egg (펫)":
            with open('EggSummonConfig.json', 'r', encoding='utf-8') as f: config = json.load(f)
            with open('PetLibrary.json', 'r', encoding='utf-8') as f: library = json.load(f)
        elif mode == "Mount (탈것)":
            with open('MountSummonConfig.json', 'r', encoding='utf-8') as f: config = json.load(f)
            with open('MountLibrary.json', 'r', encoding='utf-8') as f: library = json.load(f)
        else:
            with open('SkillSummonConfig.json', 'r', encoding='utf-8') as f: config = json.load(f)
            with open('SkillLibrary.json', 'r', encoding='utf-8') as f: library = json.load(f)
        return config, library
    except FileNotFoundError:
        return None, None

def init_session():
    if 'current_seed' not in st.session_state:
        st.session_state.current_seed = 0
        st.session_state.current_level = 0
        st.session_state.current_count = 0
        st.session_state.extra_chance = 0.0
        st.session_state.all_pulls = []
        st.session_state.batches = []
        st.session_state.is_initialized = False

init_session()

left_col, right_col = st.columns([1, 3], gap="large")

with left_col:
    st.header("설정")
    selected_mode = st.radio("모드", ["Egg (펫)", "Mount (탈것)", "Skill (스킬)"])
    
    st.markdown("---")
    seed_input = st.text_input("Seed (HEX16)", value="9665DD1A85C32F4B")
    state_input = st.text_input("Level/Count (HEX16)", value="000000000000000C")
    
    if selected_mode == "Skill (스킬)":
        chance_input = 0
        st.info("안내: 스킬 모드에서는 추가 소환 확률이 적용되지 않습니다.")
    else:
        chance_input = st.number_input(
            "추가 소환 확률 (%)", 
            min_value=0, 
            max_value=100, 
            value=16, 
            step=2, 
            format="%d"
        )
    
    if st.button("적용", use_container_width=True):
        try:
            state_val = int(state_input, 16)
            st.session_state.current_seed = int(seed_input, 16)
            st.session_state.current_level = (state_val >> 32) & 0xFFFFFFFF
            st.session_state.current_count = state_val & 0xFFFFFFFF
            st.session_state.extra_chance = float(chance_input) 
            
            st.session_state.all_pulls = []
            st.session_state.batches = []
            st.session_state.is_initialized = True
            st.session_state.current_mode = selected_mode
        except ValueError:
            st.error("입력값이 올바르지 않습니다.")
            
    # ====== [다운로드 버튼 추가 영역] ======
    st.markdown("---")
    st.markdown("#### 🛠️ 보조 도구")
    
    try:
        with open("fm_seedfinder.lua", "r", encoding="utf-8") as f:
            lua_code = f.read()
            
        st.download_button(
            label="📥 시드 추적 스크립트 다운로드",
            data=lua_code,
            file_name="fm_seedfinder.lua",
            mime="text/plain",
            use_container_width=True
        )
        st.caption("GameGuardian용 시드 자동 추출 스크립트 (.lua)")
    except FileNotFoundError:
        st.caption("스크립트 파일을 찾을 수 없습니다. (fm_seedfinder.lua)")

with right_col:
    st.title(f"시뮬레이터: {selected_mode}")

    if st.session_state.is_initialized and st.session_state.get('current_mode') != selected_mode:
        st.warning("모드가 변경되었습니다. 좌측의 '적용' 버튼을 눌러주세요.")
        st.stop()

    config, library = load_data(selected_mode)
    if not config:
        st.error("데이터 파일을 찾을 수 없습니다.")
        st.stop()

    if not st.session_state.is_initialized:
        st.info("좌측 패널에서 시드값을 입력하고 적용을 눌러주세요.")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("레벨 (Lv)", f"{st.session_state.current_level + 1}")
    c2.metric("카운트", f"{st.session_state.current_count}")
    c3.metric("추가 확률", f"{int(st.session_state.extra_chance)}%" if selected_mode != "Skill (스킬)" else "-")
    c4.metric("현재 Seed", f"{st.session_state.current_seed:016X}")

    st.markdown("---")

    btn_col1, btn_col2 = st.columns([1, 5])
    with btn_col1:
        summon_multiplier = st.selectbox("배수", [1, 15, 50], label_visibility="collapsed")
    with btn_col2:
        trigger_summon = st.button(f"Summon x{summon_multiplier}", type="primary", use_container_width=True)

    def run_summon(batch_size):
        levels_config = config["Levels"]
        rarities = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]
        
        items_by_rarity = {r: [] for r in rarities}
        if selected_mode == "Skill (스킬)":
            for k, v in library.items():
                items_by_rarity[v["Rarity"]].append(k)
        else:
            for k, v in sorted(library.items(), key=lambda x: x[1].get("MountId", x[1].get("PetId"))["Id"]):
                r = v.get("MountId", v.get("PetId"))["Rarity"]
                items_by_rarity[r].append(k)

        current_idx = 0
        total_target = batch_size
        batch_items = []
        
        # 순번 계산 버그 수정 (기존 전체 리스트의 길이를 기준으로 시작)
        start_total = len(st.session_state.all_pulls)

        while current_idx < total_target:
            pcg = MetaplayPCG(st.session_state.current_seed)
            is_bonus = current_idx >= batch_size

            if selected_mode == "Skill (스킬)":
                pcg._next_pcg32() 
            else:
                if not is_bonus:
                    bonus_roll = pcg._next_pcg32()
                    chance_raw = int(round((st.session_state.extra_chance / 100.0) * 4294967296))
                    if bonus_roll < chance_raw:
                        total_target += 1

            rarity_roll = pcg._next_pcg32()
            lvl_idx = min(st.session_state.current_level, len(levels_config) - 1)
            current_lvl_data = levels_config[lvl_idx]
            
            acc = 0
            rolled_rarity = "Common"
            for rarity in rarities:
                acc += int(round(current_lvl_data.get(rarity, 0.0) * 4294967296))
                if rarity_roll < acc:
                    rolled_rarity = rarity
                    break

            avail_items = items_by_rarity[rolled_rarity]
            
            if selected_mode == "Skill (스킬)":
                chosen_item = pcg.choice(avail_items)
                result_dict = {
                    "순번": start_total + len(batch_items) + 1,
                    "등급": RARITY_KOR[rolled_rarity],
                    "스킬 이름": chosen_item,
                    "보너스": "Y" if is_bonus else "",
                    "_r_eng": rolled_rarity,
                    "_r_score": RARITY_SCORE[rolled_rarity]
                }
            else:
                chosen_idx = pcg.next_int(len(avail_items))
                chosen_item = avail_items[chosen_idx]
                pcg.next_guid()

                num_subs = 2 if rolled_rarity in ["Legendary", "Ultimate", "Mythic"] else 1
                available_stats = list(SUBSTATS_POOL)
                stats_display = []
                stat_values = {}
                f64_sum = 0.0
                
                for _ in range(num_subs):
                    s_idx = pcg.next_int(len(available_stats))
                    s_name = available_stats.pop(s_idx)
                    f64_val = pcg.next_f64()
                    f64_sum += f64_val
                    s_val = get_substat_value(s_name, f64_val)
                    stats_display.append(f"{s_name}: +{s_val*100:.2f}%")
                    stat_values[s_name] = s_val * 100.0

                perf = (f64_sum / num_subs) * 100.0
                item_data = library[chosen_item]
                pet_type = item_data.get("Type", "-") if selected_mode == "Egg (펫)" else "-"

                result_dict = {
                    "순번": start_total + len(batch_items) + 1,
                    "등급": RARITY_KOR[rolled_rarity],
                    "타입": pet_type,
                    "스탯 1": stats_display[0] if len(stats_display) > 0 else "-",
                    "스탯 2": stats_display[1] if len(stats_display) > 1 else "-",
                    "완성도": f"{perf:.1f}%",
                    "보너스": "Y" if is_bonus else "",
                    "_r_eng": rolled_rarity,
                    "_r_score": RARITY_SCORE[rolled_rarity],
                    "_stat_values": stat_values,
                    "_perf": perf
                }
                if selected_mode == "Mount (탈것)":
                    del result_dict["타입"]

            batch_items.append(result_dict)

            st.session_state.current_count += 1
            summons_req = current_lvl_data.get("SummonsRequired", 9999)
            if st.session_state.current_count >= summons_req:
                st.session_state.current_count -= summons_req
                st.session_state.current_level += 1
                
            st.session_state.current_seed += 1
            current_idx += 1
            
        end_total = start_total + len(batch_items)
        
        st.session_state.all_pulls.extend(batch_items)
        st.session_state.batches.append({
            "size": batch_size,
            "acquired": len(batch_items),
            "start_idx": start_total + 1,
            "end_idx": end_total,
            "df": pd.DataFrame(batch_items)
        })

    if trigger_summon:
        run_summon(summon_multiplier)

    if st.session_state.all_pulls:
        with st.expander("누적 소환 요약", expanded=True):
            scol1, scol2 = st.columns(2)
            
            with scol1:
                st.markdown("#### 등급별 획득 수")
                r_counts = {r: 0 for r in ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]}
                for p in st.session_state.all_pulls:
                    r_counts[p['_r_eng']] += 1
                    
                for r in reversed(list(r_counts.keys())):
                    if r_counts[r] > 0:
                        st.markdown(f"- **{RARITY_KOR[r]}** : {r_counts[r]}개")
                        
            with scol2:
                if selected_mode == "Skill (스킬)":
                    st.markdown("#### 획득한 스킬 목록")
                    s_counts = {}
                    for p in st.session_state.all_pulls:
                        name = p['스킬 이름']
                        if name not in s_counts:
                            s_counts[name] = {'c': 0, 'score': p['_r_score'], 'r_kor': p['등급']}
                        s_counts[name]['c'] += 1
                        
                    for name, data in sorted(s_counts.items(), key=lambda x: x[1]['score'], reverse=True):
                        st.markdown(f"- [{data['r_kor']}] {name} : {data['c']}개")
                else:
                    max_score = max([p['_r_score'] for p in st.session_state.all_pulls])
                    max_r_kor = [p['등급'] for p in st.session_state.all_pulls if p['_r_score'] == max_score][0]
                    
                    st.markdown(f"#### 최고 등급({max_r_kor}) 유효 스탯 상위 9개 개체")
                    
                    valid_stats = st.multiselect(
                        "유효 스탯 필터 선택 (미선택 시 전체 스탯 기준)", 
                        options=sorted(SUBSTATS_POOL),
                        default=[]
                    )
                    
                    filtered_pulls = []
                    for p in st.session_state.all_pulls:
                        if p['_r_score'] == max_score:
                            if valid_stats:
                                match_stats = {k: v for k, v in p['_stat_values'].items() if k in valid_stats}
                                if match_stats:
                                    p_score = sum(match_stats.values())
                                    filtered_pulls.append((p_score, p))
                            else:
                                filtered_pulls.append((p['_perf'], p))
                    
                    filtered_pulls.sort(key=lambda x: x[0], reverse=True)
                    top_9_pulls = filtered_pulls[:9]
                    
                    if top_9_pulls:
                        for rank, (score, p) in enumerate(top_9_pulls, 1):
                            stats_str = " / ".join([f"{k} (+{v:.2f}%)" for k, v in p['_stat_values'].items()])
                            st.markdown(f"{rank}위. [순번 {p['순번']}번 알] {stats_str} (완성도: {p['완성도']})")
                    else:
                        st.caption("필터 조건에 부합하는 개체가 없습니다.")

    def color_rarity(val):
        eng_key = [k for k, v in RARITY_KOR.items() if v == val]
        if eng_key:
            color = WEB_RARITY_COLOR.get(eng_key[0], "white")
            return f'color: {color}; font-weight: bold;'
        return ''

    if st.session_state.batches:
        st.markdown("<br>---", unsafe_allow_html=True)
        
        st.markdown("#### 소환 결과 필터")
        filter_rarities = st.multiselect(
            "결과창에 표시할 등급을 선택하세요 (미선택 시 전체 표시)",
            options=[RARITY_KOR[r] for r in ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]],
            default=[]
        )
        
        for i, batch in enumerate(reversed(st.session_state.batches)):
            is_expanded = (i == 0) 
            
            df_filtered = batch['df'].copy()
            if filter_rarities:
                df_filtered = df_filtered[df_filtered['등급'].isin(filter_rarities)]
                
            title = f"{batch['size']}회 소환 결과 (표시 개수: {len(df_filtered)} / {batch['acquired']}개) | 누적 {batch['start_idx']} ~ {batch['end_idx']}번째"
            
            with st.expander(title, expanded=is_expanded):
                if df_filtered.empty:
                    st.caption("해당 등급의 소환 결과가 없습니다.")
                else:
                    display_cols = [c for c in df_filtered.columns if not c.startswith('_')]
                    df_to_show = df_filtered[display_cols]
                    
                    st.dataframe(
                        df_to_show.style.map(color_rarity, subset=['등급']),
                        use_container_width=True,
                        hide_index=True,
                        height=min(400, len(df_to_show) * 35 + 40)
                    )