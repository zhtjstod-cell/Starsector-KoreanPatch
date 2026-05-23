# Starsector KoreanPatch

Starsector `0.98a-RC8` Korean localization patch.

## Download

Use the ZIP attached to the latest GitHub Release. Extract it into your Starsector `mods` folder so the final path looks like:

```text
Starsector/
  mods/
    KoreanPatch/
      mod_info.json
      install_korean_patch.bat
```

## Install

1. Install Python 3 if `python --version` does not work in Command Prompt or PowerShell.
2. Run `mods/KoreanPatch/install_korean_patch.bat`.
3. Start Starsector.

The installer enables the mod automatically and patches the required core JAR/font/tips files. Backups are created next to the original files using the `.bak` suffix.

## Uninstall

Run:

```text
mods/KoreanPatch/uninstall_korean_patch.bat
```

This restores the backed-up core JAR/font/tips files. It does not delete the mod folder.

## Notes

- This repository does not include Starsector game JAR files.
- The installer applies patch data against the user's installed copy of Starsector.
- If the game version changes, the installer attempts to sync `mod_info.json` to the detected installed game version.
- Newly added English text from future Starsector updates will still require translation work.
