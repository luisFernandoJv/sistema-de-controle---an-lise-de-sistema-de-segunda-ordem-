; Script de instalação do Sistema de Controle
; Criado com Inno Setup

#define MyAppName "Sistema de Controle"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Luís Fernando Alves"
#define MyAppExeName "SistemaControle.exe"
#define MyAppIcon "image\icons\papel.ico"

[Setup]
; Informações básicas
; Fixed AppId by properly closing the GUID
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=SistemaControleSetup
SetupIconFile={#MyAppIcon}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

; Privilégios
PrivilegesRequired=admin

; Idiomas
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos adicionais:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Criar atalho na Barra de Tarefas"; GroupDescription: "Atalhos adicionais:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "ico.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "image\*"; DestDir: "{app}\image"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\image\icons\papel.ico"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\image\icons\papel.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\image\icons\papel.ico"; Tasks: quicklaunchicon

[Run]
; Fixed [Run] section - replaced "Name" with "Filename"
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
