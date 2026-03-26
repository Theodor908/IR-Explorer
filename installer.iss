; IR Explorer Inno Setup Script
; Compile this with Inno Setup 6 (https://jrsoftware.org/isinfo.php)

[Setup]
AppId={{B8A3F2E1-4C5D-6E7F-8A9B-0C1D2E3F4A5B}}
AppName=IR Explorer
AppVersion=1.0.0
AppPublisher=IR Explorer
DefaultDirName={autopf}\IR Explorer
DefaultGroupName=IR Explorer
OutputDir=installer_output
OutputBaseFilename=IR_Explorer_Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=ir_explorer\assets\icon.ico
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\IR Explorer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\IR Explorer"; Filename: "{app}\IR Explorer.exe"
Name: "{group}\Uninstall IR Explorer"; Filename: "{uninstallexe}"
Name: "{autodesktop}\IR Explorer"; Filename: "{app}\IR Explorer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\IR Explorer.exe"; Description: "Launch IR Explorer"; Flags: nowait postinstall skipifsilent
