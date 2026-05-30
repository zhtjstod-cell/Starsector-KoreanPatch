# Starsector KoreanPatch

기준 게임 버전: `0.98a-RC8`

설치 스크립트는 설치 대상 게임에서 버전을 감지해 `mod_info.json`의 `gameVersion`을 자동으로 맞춥니다.

## 설치

1. `KoreanPatch` 폴더를 Starsector의 `mods` 폴더 안에 넣습니다.
2. `KoreanPatch/install_korean_patch.bat`을 실행합니다.
3. 게임을 실행합니다. 설치 스크립트가 `enabled_mods.json`에 `KoreanPatch`를 자동 추가합니다.

Python 3이 필요합니다. 설치 BAT는 Windows Python Launcher인 `py -3`을 먼저 사용하고, 없을 때만 실제 Python 3 `python` 명령을 확인합니다. `python --version`이 버전 없이 `Python`만 출력되는 환경에서도 `py` 런처가 있으면 그대로 실행됩니다.

## 왜 설치 스크립트가 필요한가

Starsector의 일부 문구와 메인 메뉴/설정 UI 폰트는 모드 데이터 파일만으로 바꿀 수 없어서 `starsector-core`의 JAR와 코어 폰트를 패치해야 합니다. 설치 스크립트는 바닐라 JAR와 개발 작업본의 클래스 상수풀 차이만 적용하며, 원본 JAR 전체를 포함하지 않습니다. 설치 시 모드에 포함된 폰트 세트를 코어 폰트 폴더에도 반영해 Codex/툴팁 화면의 영문·한글 폰트 차이를 줄입니다.

스크립트는 처음 실행할 때 다음 백업을 만듭니다.

- `starsector-core/starfarer_obf.jar.bak`
- `starsector-core/starfarer.api.jar.bak`
- 교체되는 코어 폰트의 `.bak` 파일
- `starsector-core/data/strings/tips.json.bak`

## 복구

`KoreanPatch/uninstall_korean_patch.bat`을 실행하면 위 백업에서 JAR와 코어 폰트를 복원합니다.
