# Overwriting Mod Localization (Local Testing)

This guide explains how to manually overwrite the Steam Workshop mod's localization files with the latest translations from this repository before an official mod update is released on Steam Workshop.

---

## Mod Directory Locations

The Steam Workshop ID for **Galactic Behemoths** is `3057941504` (Stellaris App ID: `281990`).

Depending on your operating system, the mod directory is typically located at:

* **macOS**:
  ```text
  ~/Library/Application Support/Steam/steamapps/workshop/content/281990/3057941504
  ```
* **Windows**:
  ```text
  C:\Program Files (x86)\Steam\steamapps\workshop\content\281990\3057941504
  ```
  *(If your Steam library is installed on another drive or folder, replace `C:\Program Files (x86)\Steam` with your custom library path, e.g. `D:\SteamLibrary\steamapps\workshop\content\281990\3057941504`)*
* **Linux**:
  ```text
  ~/.local/share/Steam/steamapps/workshop/content/281990/3057941504
  ```
  *(Or `~/.steam/steam/steamapps/workshop/content/281990/3057941504`, or `~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/workshop/content/281990/3057941504` if running Steam via Flatpak)*

---

## Warning: Steam Updates Will Overwrite Local Changes

> [!WARNING]
> **Steam Workshop Update Notice**:
> Whenever the mod receives an official update on Steam Workshop, Steam will automatically download the new workshop files and **completely overwrite your local modifications** in that directory.
> 
> If you notice that in-game translations have reverted to an older workshop version after an update, simply re-apply the overwrite procedure described below until the latest translations are officially merged into the upstream release.

---

## Method 1: Using File Manager (GUI)

### macOS (Finder)
1. Open **Finder**.
2. Press <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd> (or choose **Go > Go to Folder...** from the menu bar).
3. Paste the mod's localization folder path:
   ```text
   ~/Library/Application Support/Steam/steamapps/workshop/content/281990/3057941504/localisation
   ```
4. In another Finder window, navigate to the `localisation/` folder of this repository (`gtsra_l10n`).
5. Copy the `english` folder from the repository and paste it into the mod's `localisation/` folder.
6. When prompted by Finder, select **Replace** to overwrite the existing English files.
7. *(Optional)* If changes were made to override files in `localisation/replace/english/`, copy that folder and replace the corresponding folder in the mod's `localisation/replace/english/`.

### Windows (File Explorer)
1. Open **File Explorer** (<kbd>Win</kbd> + <kbd>E</kbd>).
2. Navigate to the mod's localization directory:
   ```text
   C:\Program Files (x86)\Steam\steamapps\workshop\content\281990\3057941504\localisation
   ```
   *(Adjust drive letter and path according to your Steam installation).*
3. In a second File Explorer window, navigate to this repository's `localisation\` directory.
4. Copy the `english` folder from the repository into the mod's `localisation\` folder.
5. When Windows prompts you, choose **Replace the files in the destination**.
6. *(Optional)* If `localisation\replace\english\` files were changed, copy and replace them under `localisation\replace\english\` in the mod directory as well.

### Linux (File Manager)
1. Open your desktop file manager (e.g., Nautilus, Dolphin, or Thunar).
2. Press <kbd>Ctrl</kbd> + <kbd>H</kbd> to ensure hidden files and directories are visible.
3. Navigate to:
   ```text
   ~/.local/share/Steam/steamapps/workshop/content/281990/3057941504/localisation
   ```
4. Copy the `english/` folder from this repository into the mod's `localisation/` folder, confirming file replacement when prompted.
5. *(Optional)* Copy `localisation/replace/english/` to the mod's `localisation/replace/english/` if override files were modified.

---

## Method 2: Using Terminal (CLI)

Run these commands from the root directory of the `gtsra_l10n` repository.

### macOS
```bash
# Set mod directory path
MOD_DIR="$HOME/Library/Application Support/Steam/steamapps/workshop/content/281990/3057941504"

# Overwrite main English localization files
cp -R localisation/english/ "$MOD_DIR/localisation/english/"

# (Optional) Overwrite English replacement localization files
cp -R localisation/replace/english/ "$MOD_DIR/localisation/replace/english/"
```

### Linux
```bash
# Set mod directory path (adjust if using Flatpak or a custom library)
MOD_DIR="$HOME/.local/share/Steam/steamapps/workshop/content/281990/3057941504"

# Overwrite main English localization files
cp -R localisation/english/ "$MOD_DIR/localisation/english/"

# (Optional) Overwrite English replacement localization files
cp -R localisation/replace/english/ "$MOD_DIR/localisation/replace/english/"
```

### Windows (PowerShell)
```powershell
# Set mod directory path (adjust drive/library path if needed)
$ModDir = "C:\Program Files (x86)\Steam\steamapps\workshop\content\281990\3057941504"

# Overwrite main English localization files
Copy-Item -Path "localisation\english\*" -Destination "$ModDir\localisation\english\" -Recurse -Force

# (Optional) Overwrite English replacement localization files
Copy-Item -Path "localisation\replace\english\*" -Destination "$ModDir\localisation\replace\english\" -Recurse -Force
```

---

## Verification

1. Launch **Stellaris** via the Paradox Launcher.
2. Verify that **Galactic Behemoths** is enabled in your active playset.
3. Launch the game in English to test and verify the updated localization strings.
