#define MyAppName "SupportFlow AI"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "b0realnite"
#define MyAppURL "https://github.com/wasatnight/supportflow-ai"
#define MyAppExeName "SupportFlowAI.exe"

[Setup]
AppId={{13C65C4C-6091-4F4D-8E7A-8ECAFD6AD9E6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={localappdata}\Programs\SupportFlowAI
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

OutputDir=output
OutputBaseFilename=SupportFlowAI-Setup-{#MyAppVersion}
SetupIconFile=..\assets\SupportFlowAI.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

CloseApplications=yes
RestartApplications=no
SetupLogging=yes

VersionInfoVersion=0.1.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Instalador de {#MyAppName}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion=0.1.0.0

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; \
    Description: "Crear un acceso directo en el escritorio"; \
    GroupDescription: "Accesos directos:"; \
    Flags: unchecked

[Files]
Source: "..\release\SupportFlowAI\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

Source: "..\assets\SupportFlowAI.ico"; \
    DestDir: "{app}\assets"; \
    Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\assets\SupportFlowAI.ico"; \
    IconIndex: 0

Name: "{autodesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\assets\SupportFlowAI.ico"; \
    IconIndex: 0; \
    Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "Abrir {#MyAppName}"; \
    WorkingDir: "{app}"; \
    Flags: nowait postinstall skipifsilent