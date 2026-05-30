# Starsector Korean Patch 0.98a-RC8 preview6

Python launcher/PATH hotfix.

## Changes

- `install_korean_patch.bat` and `uninstall_korean_patch.bat` no longer depend only on the `python` command.
- The BAT files now try Windows Python Launcher `py -3` first.
- If `py -3` is unavailable, they validate that `python` is a real Python 3 executable before using it.
- This avoids the Windows Store alias/PATH case where `python --version` only prints `Python` without a version and the installer fails.

## Install

1. Extract `KoreanPatch_0.98a-RC8_kr_preview6.zip`.
2. Put the `KoreanPatch` folder under Starsector `mods`.
3. Run `KoreanPatch\install_korean_patch.bat`.

## Notes

- Existing preview5 translation contents are otherwise unchanged.
- Python 3 is still required, but users should no longer need to manually edit BAT files to point at a Python executable.
