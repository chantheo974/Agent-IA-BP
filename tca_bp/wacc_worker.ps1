param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputPath,
    [Parameter(Mandatory=$true)][string]$ReceiptPath
)
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$excelInstance = $null
$book = $null
$sheet = $null
$ownedConfirmed = $false
$started = [DateTime]::UtcNow
function Emit($value) { [Console]::WriteLine(($value | ConvertTo-Json -Depth 8 -Compress)); [Console]::Out.Flush() }
function Numeric($value) {
    return (($value -is [double] -or $value -is [int] -or $value -is [decimal]) -and
            -not [double]::IsNaN([double]$value) -and -not [double]::IsInfinity([double]$value))
}
function AssertFinal($expectedFingerprint, $expectedCandidate, $stage) {
    foreach ($address in @('D8','D9','D135','D136','D137','D40')) {
        if (-not (Numeric $sheet.Range($address).Value2)) { throw ('Valeur finale non numérique : ' + $address) }
    }
    $actualCandidate = [double]$sheet.Range('D136').Value2
    $calculated = [double]$sheet.Range('D135').Value2
    $residual = [double]$sheet.Range('D137').Value2
    $equity = [double]$sheet.Range('D40').Value2
    $fingerprint = $sheet.Range('D155').Value2
    if ($fingerprint -isnot [string] -or [string]::IsNullOrEmpty($fingerprint) -or $fingerprint -ne $expectedFingerprint -or
        $sheet.Range('D138').Value2 -ne 'OK' -or $sheet.Range('D107').Value2 -ne 'Itération' -or $equity -le 0 -or
        $actualCandidate -le ([double]$sheet.Range('D8').Value2 + 1e-6) -or $calculated -le ([double]$sheet.Range('D8').Value2 + 1e-6) -or
        [Math]::Abs($actualCandidate - $expectedCandidate) -gt 1e-12 -or [Math]::Abs($residual) -gt 1e-10 -or
        [Math]::Abs($calculated - $actualCandidate - $residual) -gt 1e-12 -or $excelInstance.CalculationState -ne 0 -or $excelInstance.Iteration) {
        $diagnostic = @{stage=$stage; candidate=$actualCandidate; calculated=$calculated; residual=$residual;
                        expected_candidate=$expectedCandidate; positive_equity=($equity -gt 0);
                        fingerprint_matches=($fingerprint -eq $expectedFingerprint);
                        validity=$sheet.Range('D138').Value2; mode=$sheet.Range('D107').Value2;
                        calculation_state=[int]$excelInstance.CalculationState; iteration=[bool]$excelInstance.Iteration}
        throw ('Vérification finale WACC en échec : ' + ($diagnostic | ConvertTo-Json -Compress))
    }
}
try {
    $sourceFile = (Resolve-Path -LiteralPath $InputPath).Path
    if ([IO.Path]::GetFullPath($OutputPath) -eq $sourceFile) { throw 'Source et destination identiques.' }
    if ((Test-Path -LiteralPath $OutputPath) -or (Test-Path -LiteralPath $ReceiptPath)) { throw 'Destination existante.' }
    $sourceHash = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant()
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TcaWaccWindow {
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@
    $excelInstance = New-Object -ComObject Excel.Application
    [uint32]$ownedExcelPid = 0
    [void][TcaWaccWindow]::GetWindowThreadProcessId([IntPtr]$excelInstance.Hwnd, [ref]$ownedExcelPid)
    if ($ownedExcelPid -eq 0) { throw 'Processus Excel dédié non identifié.' }
    Emit @{event='owned_process'; pid=$ownedExcelPid}
    $ownershipLine = [Console]::ReadLine()
    if ($null -eq $ownershipLine -or ($ownershipLine | ConvertFrom-Json).operation -ne 'ownership_confirmed') {
        throw 'Instance Excel non reconnue par le superviseur ; aucune modification autorisée.'
    }
    $ownedConfirmed = $true
    if ($excelInstance.Workbooks.Count -ne 0) { throw 'Instance Excel non vide : opération refusée.' }
    $excelInstance.Visible = $false
    $excelInstance.DisplayAlerts = $false
    $excelInstance.EnableEvents = $false
    $excelInstance.AskToUpdateLinks = $false
    $excelInstance.AutomationSecurity = 3
    $book = $excelInstance.Workbooks.Open($sourceFile, 0, $true)
    if ($excelInstance.Workbooks.Count -ne 1) { throw 'Un seul classeur est autorisé.' }
    $iterationInitial = [bool]$excelInstance.Iteration
    if ($iterationInitial) { throw 'Itération circulaire globale active : résolution locale refusée.' }
    $excelInstance.Calculation = 2
    $excelInstance.CalculateFullRebuild()
    $excelInstance.Calculation = -4135
    $sheet = $book.Worksheets.Item('Valorisation')
    if ($sheet.Range('D107').Value2 -ne 'Itération') { throw 'Choisir et documenter le mode Itération avant cette opération.' }
    if (-not (Numeric $sheet.Range('D9').Value2)) { throw 'Le taux IS propriétaire D9 est absent ; son relais ne constitue pas une qualification.' }
    if ($sheet.Range('D138').Value2 -ne 'OK') { throw ('Entrées WACC incomplètes : ' + $sheet.Range('D138').Value2) }
    $growth = $sheet.Range('D8').Value2
    if (-not (Numeric $growth)) { throw 'Croissance terminale absente.' }
    foreach ($address in @('D136','D141','D142','D143','D156')) {
        if ($sheet.Range($address).HasFormula -or $sheet.Range($address).Locked) { throw ('Sortie native non disponible : ' + $address) }
    }
    $initialFingerprint = $sheet.Range('D155').Value2
    if ($initialFingerprint -isnot [string] -or [string]::IsNullOrEmpty($initialFingerprint)) { throw 'Empreinte WACC absente.' }
    Emit @{event='ready'; growth=$growth; fingerprint=$initialFingerprint; excel_version=$excelInstance.Version; iteration_enabled=$iterationInitial}
    $evaluations = 0
    while ($true) {
        $line = [Console]::ReadLine()
        if ($null -eq $line) { break }
        $request = $line | ConvertFrom-Json
        if ($request.operation -eq 'abort') { Emit @{event='aborted'; source_preserved=$true}; break }
        if ($request.operation -eq 'evaluate') {
            if (++$evaluations -gt 180) { throw 'Budget de 180 évaluations dépassé.' }
            $candidate = $request.candidate
            if (-not (Numeric $candidate) -or $candidate -le $growth -or $candidate -gt 5) { throw 'Candidat hors domaine.' }
            $sheet.Range('D136').Value2 = [double]$candidate
            $sheet.Calculate()
            Emit @{event='evaluation'; validity=$sheet.Range('D138').Value2; calculated=$sheet.Range('D135').Value2;
                   equity=$sheet.Range('D40').Value2; fingerprint=[string]$sheet.Range('D155').Value2}
            continue
        }
        if ($request.operation -eq 'save') {
            if ($evaluations -lt 2 -or $request.evaluations -ne $evaluations) { throw 'Compteur de résolution incohérent.' }
            $candidate = $sheet.Range('D136').Value2
            $residual = $sheet.Range('D137').Value2
            if ($sheet.Range('D138').Value2 -ne 'OK' -or -not (Numeric $residual) -or [Math]::Abs($residual) -gt 1e-10 -or
                $sheet.Range('D40').Value2 -le 0 -or [string]$sheet.Range('D155').Value2 -ne $initialFingerprint) { throw 'Évaluation finale non admissible.' }
            # Worksheet.Calculate ne termine pas les feuilles dépendantes salies par
            # D136. La preuve globale est contrôlée après le recalcul complet ci-dessous.
            $sheet.Range('D141').Value2 = 'Convergence locale - solveur TCA sans macro'
            $sheet.Range('D142').Value2 = [double]$evaluations
            $sheet.Range('D143').Value2 = [DateTime]::UtcNow.ToOADate()
            $sheet.Range('D156').Value2 = [string]$initialFingerprint
            $excelInstance.CalculateFullRebuild()
            if ([Math]::Abs($sheet.Range('D137').Value2) -gt 1e-10 -or [string]$sheet.Range('D155').Value2 -ne $initialFingerprint) {
                throw 'Le recalcul final a modifié la solution ou ses entrées.'
            }
            AssertFinal $initialFingerprint $candidate 'after_full_rebuild'
            $book.SaveCopyAs([IO.Path]::GetFullPath($OutputPath))
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($sheet); $sheet = $null
            $book.Close($false); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book); $book = $null
            $book = $excelInstance.Workbooks.Open([IO.Path]::GetFullPath($OutputPath), 0, $true)
            $sheet = $book.Worksheets.Item('Valorisation')
            if ($sheet.Range('D107').Value2 -ne 'Itération' -or [string]$sheet.Range('D155').Value2 -ne $initialFingerprint -or
                [string]$sheet.Range('D156').Value2 -ne $initialFingerprint -or
                [Math]::Abs($sheet.Range('D136').Value2 - $candidate) -gt 1e-12 -or
                [Math]::Abs($sheet.Range('D137').Value2) -gt 1e-10) { throw 'Vérification après réouverture en échec.' }
            $excelInstance.CalculateFullRebuild()
            AssertFinal $initialFingerprint $candidate 'after_reopen_rebuild'
            if ((Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sourceHash) { throw 'Source modifiée.' }
            $receipt = @{status='CONVERGENCE_LOCALE'; algorithm='tca-local-wacc/1'; method='LOCAL_SCALAR_SOLVER';
                         application='Microsoft Excel'; version=$excelInstance.Version; candidate=$candidate;
                         mode=$sheet.Range('D107').Value2; validity=$sheet.Range('D138').Value2;
                         calculated=$sheet.Range('D135').Value2; residual=$sheet.Range('D137').Value2; equity=$sheet.Range('D40').Value2;
                         fingerprint=$initialFingerprint; evaluations=$evaluations; macros_enabled=$false; wacc_macro='NON_EXECUTEE';
                         iteration_enabled=[bool]$excelInstance.Iteration; save_reopen_verified=$true; source_preserved=$true;
                         calculation_state=[int]$excelInstance.CalculationState; sensitivity_tables='NON_VERIFIEES';
                         source_sha256=$sourceHash; output_sha256=(Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLowerInvariant();
                         started_at_utc=$started.ToString('o'); completed_at_utc=[DateTime]::UtcNow.ToString('o');
                         global_uniqueness_proven=$false; written_outputs=@('D136','D141','D142','D143','D156')}
            $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
            Emit @{event='saved'; status='CONVERGENCE_LOCALE'}
            break
        }
        throw 'Opération inconnue : seules evaluate, save et abort sont autorisées.'
    }
} catch {
    Emit @{event='error'; error=($_.Exception.Message + ' (ligne ' + $_.InvocationInfo.ScriptLineNumber + ')')}
    exit 2
} finally {
    if ($null -ne $sheet) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($sheet) }
    if ($null -ne $book) { $book.Close($false); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book) }
    if ($null -ne $excelInstance) {
        if ($ownedConfirmed) { $excelInstance.Quit() }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excelInstance)
    }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
