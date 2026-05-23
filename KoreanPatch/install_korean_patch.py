from __future__ import annotations

import base64
import hashlib
import json
import re
import shutil
import struct
import sys
import zipfile
from collections import OrderedDict, defaultdict
from pathlib import Path


MOD_ID = "KoreanPatch"
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


def read_u2(buf: bytes, pos: int) -> int:
    return struct.unpack_from(">H", buf, pos)[0]


def patch_class(data: bytes, changes: list[tuple[int, bytes, bytes]], name: str) -> tuple[bytes, int, int]:
    if data[:4] != b"\xca\xfe\xba\xbe":
        raise RuntimeError(f"Not a class file: {name}")

    by_index = {idx: (old, new) for idx, old, new in changes}
    cp_count = read_u2(data, 8)
    pos = 10
    out = bytearray(data[:10])
    changed = 0
    already = 0
    index = 1

    while index < cp_count:
        entry_start = pos
        tag = data[pos]
        pos += 1
        if tag == 1:
            length = read_u2(data, pos)
            pos += 2
            raw = data[pos:pos + length]
            pos += length
            patch = by_index.get(index)
            if patch is not None:
                old, new = patch
                if raw == old:
                    raw = new
                    changed += 1
                elif raw == new:
                    already += 1
                else:
                    raise RuntimeError(f"{name}: constant mismatch at #{index}")
            out.append(tag)
            out.extend(struct.pack(">H", len(raw)))
            out.extend(raw)
        else:
            if tag in (3, 4):
                size = 4
            elif tag in (5, 6):
                size = 8
                index += 1
            elif tag in (7, 8, 16, 19, 20):
                size = 2
            elif tag in (9, 10, 11, 12, 18):
                size = 4
            elif tag == 15:
                size = 3
            else:
                raise RuntimeError(f"{name}: unknown constant-pool tag {tag} at #{index}")
            out.extend(data[entry_start:pos + size])
            pos += size
        index += 1

    out.extend(data[pos:])
    return bytes(out), changed, already


def read_patch_map(path: Path):
    result = defaultdict(lambda: defaultdict(list))
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            jar, cls, idx, old, new = line.split("\t")
            result[jar][cls].append((int(idx), base64.b64decode(old), base64.b64decode(new)))
    return result


def read_class_replacements(path: Path):
    result = defaultdict(dict)
    if not path.exists():
        return result
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            jar, cls, old_sha, new_sha, new_b64 = line.split("\t")
            result[jar][cls] = (old_sha, new_sha, base64.b64decode(new_b64))
    return result


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patch_jar(jar: Path, jar_map, replacements=None) -> None:
    replacements = replacements or {}
    backup = jar.with_name(jar.name + ".bak")
    if not backup.exists():
        shutil.copy2(jar, backup)
        print(f"백업 생성: {backup}")
    else:
        shutil.copy2(backup, jar)
        print(f"백업에서 원본 복원: {jar.name}")

    with zipfile.ZipFile(jar, "r") as zin:
        names = zin.namelist()
        data = OrderedDict((name, zin.read(name)) for name in names)

    total_changed = 0
    total_already = 0
    replaced = 0
    replace_already = 0
    for cls, (old_sha, new_sha, new_data) in replacements.items():
        if cls not in data:
            raise RuntimeError(f"{jar.name}: class missing: {cls}")
        current_sha = sha256(data[cls])
        if current_sha == old_sha:
            data[cls] = new_data
            replaced += 1
        elif current_sha == new_sha:
            replace_already += 1
        else:
            raise RuntimeError(f"{jar.name}: class hash mismatch: {cls}")

    for cls, changes in jar_map.items():
        if cls in replacements:
            continue
        if cls not in data:
            raise RuntimeError(f"{jar.name}: class missing: {cls}")
        patched, changed, already = patch_class(data[cls], changes, cls)
        data[cls] = patched
        total_changed += changed
        total_already += already

    tmp = jar.with_suffix(jar.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as zout:
        for name, content in data.items():
            zout.writestr(name, content)
    tmp.replace(jar)

    with zipfile.ZipFile(jar, "r") as check:
        bad = check.testzip()
    if bad is not None:
        raise RuntimeError(f"{jar.name}: zip integrity failed at {bad}")
    print(f"{jar.name}: exact patch changed={total_changed} already={total_already} replaced={replaced} replace_already={replace_already}")


def copy_with_backup(src: Path, dst: Path, label: str) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    backup = dst.with_name(dst.name + ".bak")
    if dst.exists() and not backup.exists():
        shutil.copy2(dst, backup)
        print(f"{label} 백업: {backup.name}")
    shutil.copy2(src, dst)
    print(f"{label} 복사: {dst.name}")



def detect_game_version(game_root: Path) -> str | None:
    candidates = []
    obf_jar = game_root / "starsector-core" / "starfarer_obf.jar"
    backup = obf_jar.with_name(obf_jar.name + ".bak")
    for jar in (backup, obf_jar):
        if jar.exists():
            candidates.append(jar)
    pattern = re.compile(rb"\d+\.\d+[a-z](?:-RC\d+)?")
    for jar in candidates:
        try:
            with zipfile.ZipFile(jar, "r") as z:
                data = z.read("com/fs/starfarer/Version.class")
        except Exception:
            continue
        matches = sorted({m.group().decode("ascii") for m in pattern.finditer(data)}, key=len, reverse=True)
        if matches:
            return matches[0]
    descriptor = game_root / "saves"
    if descriptor.exists():
        for path in descriptor.glob("*/descriptor.xml"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            match = re.search(r"<gameVersion>([^<]+)</gameVersion>", text)
            if match:
                return match.group(1).strip()
    return None


def sync_mod_info_version(mod_root: Path, game_root: Path) -> None:
    version = detect_game_version(game_root)
    if not version:
        print("\uac8c\uc784 \ubc84\uc804 \uc790\ub3d9 \uac10\uc9c0 \uc2e4\ud328: mod_info.json\uc740 \ubcc0\uacbd\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.")
        return
    info_path = mod_root / "mod_info.json"
    try:
        info = json.loads(info_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"mod_info.json \uc77d\uae30 \uc2e4\ud328: {exc}")
        return
    info["gameVersion"] = version
    current_mod_version = str(info.get("version", ""))
    suffix_match = re.match(r"\d+\.\d+[a-z](?:-RC\d+)?(.*)", current_mod_version)
    if suffix_match:
        info["version"] = version + suffix_match.group(1)
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent="\t") + "\n", encoding="utf-8")
    print(f"\ubaa8\ub4dc \uac8c\uc784 \ubc84\uc804 \ub3d9\uae30\ud654: {version}")

def ensure_enabled(game_root: Path) -> None:
    mods_json = game_root / "mods" / "enabled_mods.json"
    data = {"enabledMods": []}
    if mods_json.exists():
        try:
            data = json.loads(mods_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            shutil.copy2(mods_json, mods_json.with_suffix(".json.bak_koreanpatch"))
    enabled = data.get("enabledMods")
    if not isinstance(enabled, list):
        enabled = []
    if MOD_ID not in enabled:
        enabled.append(MOD_ID)
    data["enabledMods"] = enabled
    mods_json.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"모드 활성화 확인: {mods_json}")


def main() -> int:
    mod_root = Path(__file__).resolve().parent
    game_root = mod_root.parent.parent
    core = game_root / "starsector-core"
    api_jar = core / "starfarer.api.jar"
    obf_jar = core / "starfarer_obf.jar"
    patch_map = read_patch_map(mod_root / "installer" / "exact_core_patch_map.tsv")
    class_replacements = read_class_replacements(mod_root / "installer" / "exact_core_class_replacements.tsv")

    print(f"게임 폴더: {game_root}")
    print(f"모드 폴더: {mod_root}")
    patch_jar(api_jar, patch_map["starfarer.api.jar"], class_replacements["starfarer.api.jar"])
    patch_jar(obf_jar, patch_map["starfarer_obf.jar"], class_replacements["starfarer_obf.jar"])

    for name in FONT_FILES:
        copy_with_backup(mod_root / "graphics" / "fonts" / name, core / "graphics" / "fonts" / name, "폰트")
    copy_with_backup(mod_root / "data" / "strings" / "tips.json", core / "data" / "strings" / "tips.json", "코어 데이터")
    sync_mod_info_version(mod_root, game_root)
    ensure_enabled(game_root)
    print("install complete: jar patch, core font/tips copy, mod version sync, and mod enablement finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
