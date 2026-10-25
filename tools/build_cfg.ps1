# Erzeugt die cfg-Dateien in common/config aus source/cfg (F-104-Werte) und der SDK-Vorlage (SimpleAircraft).
# Aufruf: powershell -File tools\build_cfg.ps1 [-Engine f104|minimal]
#   -Engine minimal: Diagnose-Triebwerk (source/cfg/engines.minimal.cfg) statt des vollen J79.
param([string]$Engine = 'f104')
$ErrorActionPreference = 'Stop'
$P   = Split-Path -Parent $PSScriptRoot
$Py  = "$P\tools\.venv\Scripts\python.exe"
$Cfg = "$P\PackageSources\SimObjects\Airplanes\pete-f104g\common\config"
$Tpl = "C:\MSFS 2024 SDK\Samples\DevmodeProjects\SimObjects\Aircraft\SimpleAircraft\PackageSources\SimObjects\Airplanes\MyCompany_Simple_Aircraft\common\config"

& $Py -I "$P\tools\merge_cfg.py" "$Tpl\flight_model.cfg" "$P\source\cfg\flight_model.f104.cfg" "$Cfg\flight_model.cfg"
& $Py -I "$P\tools\merge_cfg.py" "$Tpl\aircraft.cfg"     "$P\source\cfg\aircraft.f104.cfg"     "$Cfg\aircraft.cfg"
& $Py -I "$P\tools\merge_cfg.py" "-"                     "$P\source\cfg\engines.$Engine.cfg"   "$Cfg\engines.cfg"
& $Py -I "$P\tools\merge_cfg.py" "$Tpl\cockpit.cfg"      "$P\source\cfg\cockpit.f104.cfg"      "$Cfg\cockpit.cfg"
& $Py -I "$P\tools\merge_cfg.py" "$Tpl\systems.cfg"      "$P\source\cfg\systems.f104.cfg"      "$Cfg\systems.cfg"
"Triebwerk: engines.$Engine.cfg"
