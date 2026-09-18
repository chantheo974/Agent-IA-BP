param([Parameter(Mandatory=$true)][string]$Target)
$ErrorActionPreference = 'Stop'
$Target = (Resolve-Path -LiteralPath $Target).Path
$logRoot = Join-Path $Target 'recette-installation'
[IO.Directory]::CreateDirectory($logRoot) | Out-Null
$scripts = @(Get-ChildItem -LiteralPath $Target -Recurse -File -Filter '*.ps1')
if ($scripts.Count -ne 6) { throw ('Six scripts PowerShell attendus avant installation, trouves : ' + $scripts.Count) }
$checks = @()
foreach ($script in $scripts) {
    $tokens = $null; $parseErrors = $null
    [Management.Automation.Language.Parser]::ParseFile($script.FullName, [ref]$tokens, [ref]$parseErrors) | Out-Null
    $checks += [pscustomobject]@{file=$script.FullName.Substring($Target.Length + 1); errors=@($parseErrors | ForEach-Object {$_.Message})}
}
$checks | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $logRoot 'powershell-parser.json') -Encoding UTF8
if (@($checks | Where-Object {$_.errors.Count -gt 0}).Count -gt 0) { throw 'Un script extrait ne passe pas le parseur PowerShell.' }
$env:TCA_RECIPE_NPM_CALL_LOG = Join-Path $logRoot 'npm-attempted.txt'
function global:npm { 'npm was invoked' | Set-Content -LiteralPath $env:TCA_RECIPE_NPM_CALL_LOG; throw 'Le pack compile ne doit pas appeler npm.' }
function global:npm.cmd { 'npm.cmd was invoked' | Set-Content -LiteralPath $env:TCA_RECIPE_NPM_CALL_LOG; throw 'Le pack compile ne doit pas appeler npm.cmd.' }
& (Join-Path $Target 'Installer_TCA_BP_Web.ps1')
if (-not (Test-Path -LiteralPath (Join-Path $Target '.venv\Scripts\python.exe'))) { throw 'Environnement Python absent apres installation.' }
if (Test-Path -LiteralPath $env:TCA_RECIPE_NPM_CALL_LOG) { throw 'npm a ete appele.' }
'INSTALLER_COMPLETED_WITHOUT_NPM'
