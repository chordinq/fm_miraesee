# Miraesee Tools

게임 클라이언트 데이터를 추출하고, PC에서 소환·컬렉션·테크트리 등을 **오프라인으로 시뮬레이션**하는 도구입니다.

| 구성 | 설명 |
|------|------|
| **MiraeseeApp** | Windows GUI (`MiraeseeApp.exe` 또는 `python main.py`) |
| **miraesee_data_exporter.lua** | GameGuardian 스크립트 — 플레이어 dump를 클립보드로 복사 |

Python 설치 없이 **release zip**만 받아도 앱을 실행할 수 있습니다. Lua exporter는 GameGuardian이 있는 **Android(에뮬/실기)** 쪽에서 실행합니다.

---

## 배포판 사용법 (release zip)

`release/Miraesee-<version>-win64.zip`을 풀면 다음 파일이 있습니다.

```
MiraeseeApp.exe
_internal/                   (런타임 — exe와 같은 폴더에 유지)
assets/                      (스프라이트·설정·로컬라이제이션)
miraesee_data_exporter.lua
README.txt
```

실행 시 **PyInstaller 부트로더 스플래시**(`LoadingScreen.png`) → 메인 UI 순으로 표시됩니다. `assets/`와 `_internal/`은 exe 옆에 그대로 두세요.

### 1. 게임에서 데이터 추출 (GameGuardian)

1. 게임과 **GameGuardian**을 같은 환경(에뮬레이터 또는 루팅 기기)에서 실행합니다.
2. GameGuardian에서 **`miraesee_data_exporter.lua`** 를 스크립트로 실행합니다.
3. 안내에 따라 진행합니다. 성공하면 dump 텍스트가 **클립보드에 복사**됩니다.
   - 실패 시: 게임 재시작 후 다시 시도 (PlayerModel 주소 탐색 실패 등).
4. PC로 dump를 옮기려면 클립보드를 PC에 붙여넣거나, GG/에뮬의 클립보드 공유 기능을 사용합니다.

> dump 형식은 `[DUMP_VERSION]` … `[END]` 블록입니다. 앱 파서와 Lua exporter가 **동일한 스키마**를 사용합니다.

### 2. PC에서 dump 불러오기

1. **`MiraeseeApp.exe`** 를 실행합니다.
2. dump 텍스트를 **PC 클립보드**에 붙여 넣습니다.
3. 왼쪽 사이드 패널 하단의 **LoadDump** 버튼(↑ 화살표 아이콘)을 클릭합니다.
4. 로드가 성공하면 스킬·펫·탈것·장비·테크트리 등이 dump 기준으로 갱신됩니다.
   - 클립보드가 비어 있으면 아무 일도 일어나지 않습니다.
   - 형식 오류 시 로드 실패 메시지가 표시됩니다.

### 3. 앱 화면 구성

왼쪽 **탭**으로 카테고리를 전환합니다 (위→아래).

| 탭 | 내용 |
|----|------|
| Forge | 장비 컬렉션 |
| Skills (녹색) | 스킬 소환·업그레이드 시뮬 |
| Pets (파랑) | 펫·알 소환·부화 시뮬 |
| Mounts (주황) | 탈것 소환 시뮬 |
| Tech Tree (빨강) | 테크트리 연구·클레임 |

- **가운데**: 선택 탭의 메인 뷰 (소환 버튼, 결과 등)
- **오른쪽**: 해당 카테고리 컬렉션 그리드
- **설정(⚙)**: UI 언어 변경 (로컬라이제이션 JSON 기준)

소환·업그레이드는 **게임과 동일한 IL 포팅 로직**(`core/`)으로 처리됩니다. dump를 다시 불러오기 전까지 앱 내 변경은 **로컬 시뮬**이며 게임 계정에 반영되지 않습니다.

### 4. 자주 묻는 문제

| 증상 | 확인 |
|------|------|
| LoadDump 후 변화 없음 | PC 클립보드에 dump 전문이 있는지, `[DUMP_VERSION]`/`[END]` 포함 여부 |
| GG에서 추출 실패 | 게임 실행 중인지, 망치 값 검색·PlayerModel 추적 단계 재시도 |
| exe가 느리게 시작 | one-file exe는 첫 실행 시 임시 폴더에 풀림 — SSD·백신 예외 확인 |
| 한글이 깨짐 | 설정에서 언어를 `ko`로 변경 |

---

## 개발자: 로컬 실행

`scripts/` 디렉터리에서:

```bash
pip install -e .
python main.py
```

컴포넌트 미리보기:

```bash
python ui/test/test.py
python ui/test/test_game.py
```

의존성은 **PySide6**만 필요합니다 (`pyproject.toml`).

---

## 개발자: release zip 빌드

Windows, vanilla Python venv 권장 (Anaconda·numpy 등 불필요 패키지 없이):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[bundle]"
.\build\release.ps1
```

산출물:

```
release/Miraesee-<version>-win64.zip
dist/MiraeseeApp/MiraeseeApp.exe
dist/MiraeseeApp/_internal/
```

- **onedir** 빌드 (onefile 압축 해제 지연 없음)
- **assets**는 zip에 별도 폴더로 포함 (exe 번들 밖)
- 부트로더 **splash**는 `assets/icon.png`

exe만 빌드:

```powershell
.\build\build.ps1
```

빌드 캐시(`build/MiraeseeApp/`, `dist/`, `release/`)는 git에 포함하지 않습니다.

---

## 프로젝트 구조

| 경로 | 역할 |
|------|------|
| `core/` | C# IL 포팅 게임 로직 (순수 시뮬) |
| `config/` | JSON 매핑·설정 로더 |
| `controllers/` | Python ↔ QML 브리지 |
| `app/` | QML 엔진·세션 |
| `ui/` | QML 위젯·프리뷰 (`ui/test/`) |
| `utils/` | dump 파서, `miraesee_data_exporter.lua` |
| `assets/` | 게임 JSON, 스프라이트, 로컬라이제이션 |
| `build/` | PyInstaller spec·빌드 스크립트 (산출물 제외) |

`dump.cs`, `old_dump.cs`는 로컬 IL 참고용이며 저장소에 올리지 않습니다.
