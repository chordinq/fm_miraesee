from utils.constants import AGE_KOR_SPACED, AGE_NAME

def start_tutorial(state):
    state["tutorial_step"] = 1
    print("\n[ 🎓 튜토리얼을 시작합니다. ]")
    print("- 'quit' 또는 'return'을 입력하면 튜토리얼이 종료됩니다.")
    print("\n👉 먼저 대장간 모드에 진입해 보세요.")
    return True

def advance_tutorial(state, cmd, mode):
    step = state.get("tutorial_step", 0)
    if step == 0: return

    if step == 1 and mode == "Forge":
        print("\n👉 3회 제작을 해보고 실제 인게임 결과와 비교해보세요.")
        state["tutorial_step"] = 2
        
    elif step == 2 and cmd == "forge" and mode == "Forge":
        print("\n👉 이번에는 10000회 제작을 미리 시뮬레이션 해보세요.")
        state["tutorial_step"] = 3
        
    elif step == 3 and cmd == "forge" and mode == "Forge":
        history = state.get("Forge", {}).get("history", [])
        if history:
            # 최고 티어 및 한 단계 아래 티어를 동적으로 계산
            best_age = max(x['Age'] for x in history)
            best_m1_age = max(0, best_age - 1)
            
            state["tutorial_target_tier_kor"] = AGE_KOR_SPACED.get(best_age, "양자").strip()
            state["tutorial_target_tier_eng"] = AGE_NAME.get(best_age, "quantum").lower().strip()
            state["tutorial_target_tier_m1_kor"] = AGE_KOR_SPACED.get(best_m1_age, "다중우주").strip()
            state["tutorial_target_tier_m1_eng"] = AGE_NAME.get(best_m1_age, "multiverse").lower().strip()
            
            current_level = state["Forge"].get("level", 20)
            state["tutorial_next_level"] = min(35, current_level + 1)
            
            print("\n👉 결과를 깔끔하게 요약해 보세요.")
            state["tutorial_step"] = 4
            
    elif step == 4 and cmd == "summary" and mode == "Forge":
        best_tier_kor = state.get("tutorial_target_tier_kor", "양자")
        print(f"\n👉 {best_tier_kor} 티어 장비가 떴네요! 해당 티어 장비의 세부 스탯만 필터링해서 확인해 보세요.")
        state["tutorial_step"] = 5
        
    elif step == 5 and cmd == "search" and mode == "Forge":
        best_tier_m1_kor = state.get("tutorial_target_tier_m1_kor", "다중우주")
        print(f"\n👉 혹시 {best_tier_m1_kor} 티어에도 좋은 스탯의 무기가 있는지 확인해보세요.")
        state["tutorial_step"] = 6
        
    elif step == 6 and cmd == "search" and mode == "Forge":
        print("\n👉 만약 다음 레벨에서 소환했다면 어떨 지 테스트해봅시다.")
        print("   지금까지의 기록을 초기화하세요.")
        state["tutorial_step"] = 7
        
    elif step == 7 and cmd == "reset" and mode == "Forge":
        print("\n👉 장비를 1000번 제작해보세요.")
        state["tutorial_step"] = 8
        
    elif step == 8 and cmd == "forge" and mode == "Forge":
        next_level = state.get("tutorial_next_level", 20)
        print(f"\n👉 대장간 레벨을 {next_level}로 설정해보세요(만약 이미 최고레벨(35)이면 그냥 그대로 35)")
        state["tutorial_step"] = 9
        
    elif step == 9 and cmd == "set" and mode == "Forge":
        print("\n👉 장비를 9000번 제작해보세요.")
        state["tutorial_step"] = 10
        
    elif step == 10 and cmd == "forge" and mode == "Forge":
        print("\n👉 요약을 확인해보세요.")
        state["tutorial_step"] = 11
        
    elif step == 11 and cmd == "summary" and mode == "Forge":
        print("\n[ 튜토리얼 완료! ]")
        print("모든 기본 사용법을 익히셨습니다. 이제 자유롭게 시뮬레이터를 사용해 보세요!\n")
        print("help를 입력하시면 사용 가능한 명령어들을 확인하실 수 있습니다.")
        state["tutorial_step"] = 0

def get_tutorial_suggestion(state, text):
    if text: return None  
    
    step = state.get("tutorial_step", 0)
    mode = state.get("current_mode", "Global")
    
    if step == 1 and mode == "Global": return "mode forge"
    elif step == 2 and mode == "Forge": return "forge amount:3"
    elif step == 4 and mode == "Forge": return "summary"
    elif step == 5 and mode == "Forge": return f"search tier:{state.get('tutorial_target_tier_eng', 'quantum')}"
    elif step == 6 and mode == "Forge": return f"search tier:{state.get('tutorial_target_tier_m1_eng', 'multiverse')} perf:90 type:weapon"
    elif step == 7 and mode == "Forge": return "reset"
    elif step == 9 and mode == "Forge": return f"set level {state.get('tutorial_next_level', 20)}"
        
    return None