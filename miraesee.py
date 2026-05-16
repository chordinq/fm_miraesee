import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    os.system("")
    
    while True:
        clear_screen()
        print("\n" + "="*50)
        print("Forge Master 미래시 통합 시뮬레이터")
        print("="*50)
        print("\033[38;2;52;152;219m[실행 가능한 시뮬레이터]\033[0m")
        print("  - \033[1megg\033[0m   : 펫(Egg) 소환 미래시")
        print("  - \033[1mmount\033[0m : 탈것(Mount) 소환 미래시")
        print("  - \033[1mskill\033[0m : 스킬(Skill) 소환 미래시")
        print("\n\033[38;2;255;87;34m[시스템 명령어]\033[0m")
        print("  - \033[1mexit\033[0m  : 시뮬레이터 완전히 종료")
        print("="*50)
        
        user_cmd = input("\n원하는 모드를 입력하세요\n> ").strip().lower()
        
        if user_cmd == 'exit':
            print("프로그램을 종료합니다.")
            sys.exit()
            
        elif user_cmd == 'egg':
            try:
                import egg_summon
                print("\n[ 펫(Egg) 시뮬레이터 진입 ]\n")
                egg_summon.main() 
            except ImportError:
                print("\nError: egg_summon.py 파일을 찾을 수 없습니다.")
                input("계속하려면 엔터를 누르세요...")
                
        elif user_cmd == 'mount':
            try:
                import mount_summon
                print("\n[ 탈것(Mount) 시뮬레이터 진입 ]\n")
                mount_summon.main()
            except ImportError:
                print("\nError: mount_summon.py 파일을 찾을 수 없습니다.")
                input("계속하려면 엔터를 누르세요...")
                
        elif user_cmd == 'skill':
            try:
                import skill_summon
                print("\n[ 스킬(Skill) 시뮬레이터 진입 ]\n")
                skill_summon.main()
            except ImportError:
                print("\nError: skill_summon.py 파일을 찾을 수 없습니다.")
                input("계속하려면 엔터를 누르세요...")
                
        else:
            print("\n알 수 없는 명령어입니다. (egg, mount, skill, exit 중 입력)")
            input("계속하려면 엔터를 누르세요...")

if __name__ == "__main__":
    main()