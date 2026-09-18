param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputPath,
    [Parameter(Mandatory=$true)][string]$ReceiptPath,
    [Parameter(Mandatory=$true)][string]$SourceSha256,
    [double]$TimeoutSeconds=300,
    [switch]$IncludeTables
)
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$excelInstance = $null
$book = $null
$ownedConfirmed = $false
$started = [DateTime]::UtcNow
function Emit($value) { [Console]::WriteLine(($value | ConvertTo-Json -Depth 8 -Compress)); [Console]::Out.Flush() }
function Hash($path) { return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function AssertDone {
    while ($excelInstance.CalculationState -ne 0) {
        if (([DateTime]::UtcNow-$started).TotalSeconds -ge $TimeoutSeconds) { throw 'Délai de calcul Excel dépassé.' }
        Start-Sleep -Milliseconds 150
    }
    if ($excelInstance.Iteration -or $excelInstance.EnableEvents -or $excelInstance.AutomationSecurity -ne 3) {
        throw 'État de calcul, événements ou macros incompatible.'
    }
}
function CloseBook {
    if ($null -ne $script:book) {
        try { $script:book.Close($false) }
        finally { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($script:book); $script:book = $null }
    }
}
try {
    if ([double]::IsNaN($TimeoutSeconds) -or [double]::IsInfinity($TimeoutSeconds) -or
        $TimeoutSeconds -lt 1 -or $TimeoutSeconds -gt 3600) { throw 'Délai natif hors domaine.' }
    $sourceFile = (Resolve-Path -LiteralPath $InputPath).Path
    if ([IO.Path]::GetFullPath($OutputPath) -eq $sourceFile -or
        [IO.Path]::GetFullPath($ReceiptPath) -eq $sourceFile -or
        [IO.Path]::GetFullPath($OutputPath) -eq [IO.Path]::GetFullPath($ReceiptPath)) { throw 'Les trois chemins doivent être distincts.' }
    if ((Test-Path -LiteralPath $OutputPath) -or (Test-Path -LiteralPath $ReceiptPath)) { throw 'Destination existante.' }
    $sourceHash = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($sourceHash -ne $SourceSha256) { throw 'Source modifiée avant ouverture native.' }
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TcaRecalculationWindow {
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@
    $previousExcelPids = @(Get-Process -Name EXCEL -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $createdDedicated = $false
    $excelInstance = New-Object -ComObject Excel.Application
    [uint32]$ownedExcelPid = 0
    [void][TcaRecalculationWindow]::GetWindowThreadProcessId([IntPtr]$excelInstance.Hwnd, [ref]$ownedExcelPid)
    if ($ownedExcelPid -eq 0) { throw 'Processus Excel dédié non identifié.' }
    $createdDedicated = $ownedExcelPid -gt 0 -and ($previousExcelPids -notcontains [int]$ownedExcelPid)
    if (-not $createdDedicated) { throw 'Instance Excel existante : aucun droit de fermeture.' }
    Emit @{event='owned_process'; pid=$ownedExcelPid}
    $ack = [Console]::ReadLine()
    if ($null -eq $ack -or ($ack | ConvertFrom-Json).operation -ne 'ownership_confirmed') {
        throw 'Propriété du processus non confirmée : aucun réglage ni ouverture.'
    }
    $ownedConfirmed = $true
    if ($excelInstance.Workbooks.Count -ne 0) { throw 'Instance Excel non vide.' }
    $excelInstance.Visible = $false
    $excelInstance.DisplayAlerts = $false
    $excelInstance.EnableEvents = $false
    $excelInstance.AskToUpdateLinks = $false
    $excelInstance.AutomationSecurity = 3
    $book = $excelInstance.Workbooks.Open($sourceFile, 0, $true)
    $iterationInitial = [bool]$excelInstance.Iteration
    if ($iterationInitial) { throw 'Itération circulaire globale active : recalcul refusé.' }
    if ($excelInstance.Workbooks.Count -ne 1 -or -not $book.ReadOnly -or $excelInstance.Iteration) {
        throw 'Classeur, lecture seule ou itération globale incompatible.'
    }
    $initialCalculation = [int]$excelInstance.Calculation
    if ($IncludeTables) { $excelInstance.Calculation = -4105 } else { $excelInstance.Calculation = 2 }
    $excelInstance.CalculateFullRebuild()
    AssertDone
    # Relecture sans nouvelle exécution des tables ; leur demande n'est pas une qualification.
    $excelInstance.Calculation = 2
    AssertDone
    $book.SaveCopyAs([IO.Path]::GetFullPath($OutputPath))
    CloseBook
    $savedHash = Hash $OutputPath
    $book = $excelInstance.Workbooks.Open([IO.Path]::GetFullPath($OutputPath), 0, $true)
    if ($excelInstance.Workbooks.Count -ne 1 -or -not $book.ReadOnly) { throw 'Réouverture isolée en lecture seule non vérifiée.' }
    $excelInstance.Calculation = 2
    AssertDone
    CloseBook
    if ((Hash $sourceFile) -ne $sourceHash -or (Hash $OutputPath) -ne $savedHash) {
        throw 'La source ou la copie persistée a changé pendant la vérification.'
    }
    $result = @{
        status='RECALCULE'; application='Microsoft Excel'; version=[string]$excelInstance.Version;
        source_sha256=$sourceHash; output_sha256=$savedHash;
        started_at_utc=$started.ToString('o'); completed_at_utc=[DateTime]::UtcNow.ToString('o');
        calculation_state=0; initial_calculation_mode=$initialCalculation;
        method='CalculateFullRebuild'; sensitivity_tables=$(if ($IncludeTables) {'RECALCUL_DEMANDE'} else {'NON_VERIFIEES'});
        wacc_macro='NON_EXECUTEE'; macros_enabled=$false; economic_validation='NON_EFFECTUEE';
        events_enabled=$false; iteration_initial=$iterationInitial; iteration_enabled=$false;
        source_preserved=$true; save_reopen_verified=$true; dedicated_instance_verified=$true;
        owned_process_confirmed=$true; owned_excel_pid=$ownedExcelPid; links_update_requested=$false;
        include_tables=[bool]$IncludeTables; base_cell_writes=@(); adopted=$false
    }
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
    Emit @{event='saved'; status='RECALCULE'}
} catch {
    Emit @{event='error'; error=$_.Exception.Message}
    exit 2
} finally {
    try { CloseBook }
    finally {
        if ($null -ne $excelInstance) {
            try { if ($ownedConfirmed -or $createdDedicated) { $excelInstance.Quit() } }
            finally { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excelInstance) }
        }
        [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    }
}
