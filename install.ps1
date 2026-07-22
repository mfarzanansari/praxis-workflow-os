param(
    [Parameter(Mandatory=$true)][string]$Target,
    [switch]$DryRun,
    [switch]$Force,
    [string]$BackupDir,
    [string[]]$Include
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ArgsList = @("$ScriptDir\scripts\install.py", "--target", $Target)
if ($DryRun) { $ArgsList += "--dry-run" }
if ($Force) { $ArgsList += "--force" }
if ($BackupDir) { $ArgsList += @("--backup-dir", $BackupDir) }
foreach ($Skill in $Include) { $ArgsList += @("--include", $Skill) }

python @ArgsList
exit $LASTEXITCODE
