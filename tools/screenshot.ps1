# Bildschirmfoto in voller Auflösung (für Dev-Mode-Debugfenster, statt Steam-F12).
# Aufruf: powershell -File tools\screenshot.ps1 <ausgabe.png> [-Sim] [-Screen 0]
#   -Sim: holt das Sim-Fenster kurz in den Vordergrund und danach das vorherige Fenster (z. B. VS Code) zurück.
# Erfasst, was auf dem Bildschirm sichtbar ist (Sim im randlosen Fenster/Fenstermodus).
param([Parameter(Mandatory)][string]$Out, [switch]$Sim, [int]$Screen = 0)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type -Namespace W -Name U -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern System.IntPtr GetForegroundWindow();
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(System.IntPtr h);
[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr h, int cmd);
[DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, int flags, int extra);
'@
[W.U]::SetProcessDPIAware() | Out-Null   # sonst nur skalierte Auflösung (z. B. 2560x1440 statt 3840x2160)

function Activate($h) {
    [W.U]::keybd_event(0x12, 0, 0, 0); [W.U]::keybd_event(0x12, 0, 2, 0)   # Alt antippen, sonst blockt Windows den Fokuswechsel
    [W.U]::ShowWindow($h, 9) | Out-Null                                    # SW_RESTORE
    [W.U]::SetForegroundWindow($h) | Out-Null
}

$prev = [W.U]::GetForegroundWindow()
if ($Sim) {
    $p = Get-Process | Where-Object { $_.MainWindowTitle -match 'Flight Simulator' } | Select-Object -First 1
    if (-not $p) { throw 'Sim-Fenster nicht gefunden' }
    Activate $p.MainWindowHandle
    Start-Sleep -Milliseconds 800
}
$b = [System.Windows.Forms.Screen]::AllScreens[$Screen].Bounds
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.X, $b.Y, 0, 0, $bmp.Size)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
if ($Sim) { Activate $prev }
"{0} ({1}x{2})" -f $Out, $b.Width, $b.Height
