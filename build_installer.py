"""Build IR Explorer Windows installer.

Steps:
  1. Run PyInstaller to create the bundled app folder
  2. Generate the Inno Setup .iss script
  3. Print instructions for compiling the installer

Usage:
  python build_installer.py
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "IR Explorer"
APP_VERSION = "1.0.0"
APP_PUBLISHER = "IR Explorer"
APP_EXE = "IR Explorer.exe"
DIST_DIR = os.path.join(ROOT, "dist", "IR Explorer")
ISS_PATH = os.path.join(ROOT, "installer.iss")

# ── Step 1: PyInstaller ──

print("=" * 60)
print("Step 1: Building with PyInstaller...")
print("=" * 60)

pyinstaller_args = [
    sys.executable, "-m", "PyInstaller",
    "--name", APP_NAME,
    "--windowed",
    "--noconfirm",
    "--clean",
    "--icon", "ir_explorer/assets/icon.ico",
    # include data files
    "--add-data", f"ir_explorer/assets;ir_explorer/assets",
    "--add-data", f"ir_explorer/lessons/definitions;ir_explorer/lessons/definitions",
    # hidden imports that PyInstaller might miss
    "--hidden-import", "ir_explorer.core.evaluation",
    "--hidden-import", "ir_explorer.core.crawler",
    "--hidden-import", "ir_explorer.core.link_analysis",
    "--hidden-import", "ir_explorer.core.corpus_generator",
    "--hidden-import", "ir_explorer.lessons.animations",
    "--hidden-import", "ir_explorer.lessons.engine",
    "--hidden-import", "ir_explorer.lessons.registry",
    "--hidden-import", "yaml",
    # entry point
    "ir_explorer/main.py",
]

result = subprocess.run(pyinstaller_args, cwd=ROOT)
if result.returncode != 0:
    print("\nPyInstaller failed!")
    sys.exit(1)

print(f"\nPyInstaller output: {DIST_DIR}")

# ── Step 2: Inno Setup script ──

print("\n" + "=" * 60)
print("Step 2: Generating Inno Setup script...")
print("=" * 60)

iss_content = f"""; IR Explorer Inno Setup Script
; Compile this with Inno Setup 6 (https://jrsoftware.org/isinfo.php)

[Setup]
AppId={{{{B8A3F2E1-4C5D-6E7F-8A9B-0C1D2E3F4A5B}}}}
AppName={APP_NAME}
AppVersion={APP_VERSION}
AppPublisher={APP_PUBLISHER}
DefaultDirName={{autopf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
OutputDir={ROOT}\\installer_output
OutputBaseFilename=IR_Explorer_Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile={ROOT}\\ir_explorer\\assets\\icon.ico
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "{DIST_DIR}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_EXE}"
Name: "{{group}}\\Uninstall {APP_NAME}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_EXE}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{APP_EXE}"; Description: "Launch {APP_NAME}"; Flags: nowait postinstall skipifsilent
"""

with open(ISS_PATH, "w", encoding="utf-8") as f:
    f.write(iss_content)

print(f"Inno Setup script: {ISS_PATH}")

# ── Done ──

print("\n" + "=" * 60)
print("Done! Next steps:")
print("=" * 60)
print(f"""
1. Install Inno Setup 6 from https://jrsoftware.org/isdl.php
2. Open {ISS_PATH} in Inno Setup Compiler
3. Click Build > Compile (or press Ctrl+F9)
4. The installer will be created at: {ROOT}\\installer_output\\IR_Explorer_Setup.exe

Alternatively, compile from command line:
  "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" "{ISS_PATH}"
""")
