from __future__ import annotations

import shutil
from pathlib import Path


FONT_FILES = [
    "insignia15LTaa.fnt",
    "insignia15LTaa_0.png",
    "insignia21LTaa.fnt",
    "insignia21LTaa_0.png",
    "insignia25LTaa.fnt",
    "insignia25LTaa_0.png",
    "korean15.fnt",
    "korean15_0.png",
    "orbitron12.fnt",
    "orbitron12_0.png",
    "orbitron12condensed.fnt",
    "orbitron20aa.fnt",
    "orbitron20aa_0.png",
    "orbitron20aabold.fnt",
    "orbitron20aabold_0.png",
    "orbitron20bold.fnt",
    "orbitron20bold_0.png",
    "orbitron24aa.fnt",
    "orbitron24aa_0.png",
    "orbitron24aabold.fnt",
    "orbitron24aabold_0.png",
    "victor10.fnt",
    "victor10_0.png",
    "victor14.fnt",
    "victor14_0.png",
    "victor21.fnt",
    "victor21_0.png",
]


def restore(path: Path) -> None:
    backup = path.with_name(path.name + ".bak")
    if backup.exists():
        shutil.copy2(backup, path)
        print(f"복원: {path.name}")
    else:
        print(f"백업 없음, 스킵: {path.name}")


def main() -> int:
    mod_root = Path(__file__).resolve().parent
    game_root = mod_root.parent.parent
    core = game_root / "starsector-core"

    restore(core / "starfarer_obf.jar")
    restore(core / "starfarer.api.jar")
    for name in FONT_FILES:
        path = core / "graphics" / "fonts" / name
        backup = path.with_name(path.name + ".bak")
        if backup.exists():
            shutil.copy2(backup, path)
            print(f"폰트 복원: {name}")
        elif name.startswith("korean15") and path.exists():
            path.unlink()
            print(f"추가 폰트 제거: {name}")
    restore(core / "data" / "strings" / "tips.json")
    print("복구 완료: 모드 폴더는 삭제하지 않았습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
