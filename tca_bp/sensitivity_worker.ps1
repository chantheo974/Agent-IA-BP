param(
    [Parameter(Mandatory=$true)][string]$PlanPath,
    [Parameter(Mandatory=$true)][string]$PlanSha256,
    [Parameter(Mandatory=$true)][string]$ResumePath,
    [Parameter(Mandatory=$true)][string]$ResumeSha256,
    [Parameter(Mandatory=$true)][string]$OutputPath,
    [Parameter(Mandatory=$true)][string]$ReceiptPath,
    [switch]$ProbeOnly
)
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$excelInstance = $null; $book = $null; $sheet = $null; $ownedConfirmed = $false
$started = [DateTime]::UtcNow
$nativeMapping = $null
$sheetName = 'Sensi Analyses'
function Mapped($logicalAddress) {
    if ($null -eq $script:nativeMapping) { return $logicalAddress }
    $physical = $script:nativeMapping.cells.$logicalAddress
    if ($physical -isnot [string] -or $physical -notmatch '^[A-Z]{1,3}[1-9][0-9]{0,6}$') { throw 'Proprietaire natif absent ou invalide dans le profil.' }
    return $physical
}
function Emit($value) { [Console]::WriteLine(($value | ConvertTo-Json -Depth 12 -Compress)); [Console]::Out.Flush() }
function Hash($path) { return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function ReadSealedJson($path, $expectedHash) {
    $bytes = [IO.File]::ReadAllBytes($path)
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { $actual = ([BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $hasher.Dispose() }
    if ($actual -ne $expectedHash) { throw 'Document de campagne modifié avant ouverture native.' }
    return ([Text.Encoding]::UTF8.GetString($bytes).TrimStart([char]0xFEFF) | ConvertFrom-Json)
}
function CloseBook {
    if ($null -ne $script:sheet) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($script:sheet); $script:sheet = $null }
    if ($null -ne $script:book) {
        try { $script:book.Close($false) }
        finally { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($script:book); $script:book = $null }
    }
}
function OpenBook($path) {
    if ($excelInstance.Workbooks.Count -ne 0) { throw 'Une seule copie peut être ouverte à la fois.' }
    $script:book = $excelInstance.Workbooks.Open([IO.Path]::GetFullPath($path), 0, $true)
    if ($excelInstance.Workbooks.Count -ne 1 -or $excelInstance.Iteration) { throw 'Instance isolée ou itération globale incompatible.' }
    $script:sheet = $book.Worksheets.Item($sheetName)
}
function Number($address) {
    $range = $sheet.Range((Mapped $address))
    $functions = $excelInstance.WorksheetFunction
    try {
        $errorFlag = $functions.IsError($range)
        if ($errorFlag -isnot [bool]) {
            $typeName = if ($null -eq $errorFlag) { 'null' } else { $errorFlag.GetType().FullName }
            throw ('Type du diagnostic ISERROR non reconnu dans ' + $address + ' : ' + $typeName)
        }
        if ($errorFlag) { throw ('Erreur Excel dans ' + $address) }
        $value = $range.Value2
        if (($value -isnot [double] -and $value -isnot [int] -and $value -isnot [decimal]) -or
            [double]::IsNaN([double]$value) -or [double]::IsInfinity([double]$value)) {
            $typeName = if ($null -eq $value) { 'null' } else { $value.GetType().FullName }
            throw ('Valeur non numérique dans ' + $address + ' ; type=' + $typeName)
        }
        return $value
    } finally {
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($functions)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($range)
    }
}
function ReadValues($addresses) {
    $values = @{}
    foreach ($address in $addresses) { $values[$address] = Number $address }
    return $values
}
function AssertDrivers($expected) {
    foreach ($address in @('C8','C14','C18')) {
        if ($sheet.Range((Mapped $address)).HasFormula -or -not $sheet.Range((Mapped $address)).Locked -or
            (Number $address) -ne $expected.$address) { throw ('Pilote technique inattendu : ' + $address) }
    }
    if (-not $sheet.ProtectContents) { throw 'Protection de la feuille absente.' }
}
function AssertDone {
    if ($excelInstance.CalculationState -ne 0 -or $excelInstance.Iteration) { throw 'Calcul incomplet ou itération globale active.' }
}
try {
    $plan = ReadSealedJson $PlanPath $PlanSha256
    $resumeData = ReadSealedJson $ResumePath $ResumeSha256
    if ($plan.schema -ne 'tca-sensitivity-plan/1' -or $plan.scenarios.Count -ne 24) { throw 'Plan de recette incompatible.' }
    # Sonde de maintenance explicite : le plan reste complet et scellé, mais
    # le reçu ne peut jamais être une qualification ni une sortie adoptable.
    if ($ProbeOnly -and ($null -ne $resumeData.base -or @($resumeData.scalars).Count -ne 0)) {
        throw 'La sonde de maintenance ne peut pas reprendre une qualification.'
    }
    if ($null -ne $plan.native_mapping) {
        $nativeMapping = $plan.native_mapping
        if ($nativeMapping.schema -ne 'tca-native-mapping/1' -or $nativeMapping.kind -ne 'sensitivity' -or
            $nativeMapping.profile_sha256 -notmatch '^[a-f0-9]{64}$' -or $nativeMapping.mapping_sha256 -notmatch '^[a-f0-9]{64}$' -or
            $nativeMapping.sheet -isnot [string] -or [string]::IsNullOrWhiteSpace($nativeMapping.sheet)) { throw 'Profil natif des sensibilites incompatible.' }
        $sheetName = $nativeMapping.sheet
        foreach ($logical in @('C8','C14','C18','D24','E24','F24','G24','C39','D39','C49')) { [void](Mapped $logical) }
    }
    $sourceFile = (Resolve-Path -LiteralPath $plan.source).Path
    if ((Hash $sourceFile) -ne $plan.source_sha256 -or [IO.Path]::GetFullPath($OutputPath) -eq $sourceFile -or
        ((Test-Path -LiteralPath $OutputPath) -ne ($null -ne $resumeData.base)) -or
        (Test-Path -LiteralPath $ReceiptPath)) { throw 'Source altérée ou destination incompatible avec la reprise.' }
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TcaSensitivityWindow {
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@
    $previousExcelPids = @(Get-Process -Name EXCEL -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $createdDedicated = $false
    $excelInstance = New-Object -ComObject Excel.Application
    [uint32]$ownedExcelPid = 0
    [void][TcaSensitivityWindow]::GetWindowThreadProcessId([IntPtr]$excelInstance.Hwnd, [ref]$ownedExcelPid)
    if ($ownedExcelPid -eq 0) { throw 'Processus dédié non identifié.' }
    $createdDedicated = $ownedExcelPid -gt 0 -and ($previousExcelPids -notcontains [int]$ownedExcelPid)
    if (-not $createdDedicated) { throw 'Instance Excel existante : aucun droit de fermeture.' }
    Emit @{event='owned_process'; pid=$ownedExcelPid}
    $ack = [Console]::ReadLine()
    if ($null -eq $ack -or ($ack | ConvertFrom-Json).operation -ne 'ownership_confirmed') { throw 'Propriété du processus non confirmée.' }
    $ownedConfirmed = $true
    if ($excelInstance.Workbooks.Count -ne 0) { throw 'Instance Excel non vide.' }
    $excelInstance.Visible = $false; $excelInstance.DisplayAlerts = $false
    $excelInstance.EnableEvents = $false; $excelInstance.AskToUpdateLinks = $false
    $excelInstance.AutomationSecurity = 3
    $targets = @()
    foreach ($r in 25..33) { foreach ($c in @('D','E','F','G')) { $targets += ($c + $r) } }
    foreach ($r in 40..45) { foreach ($c in @('C','D')) { $targets += ($c + $r) } }
    foreach ($r in 50..52) { foreach ($c in @('D','E','F')) { $targets += ($c + $r) } }
    $baseRefs = @('D24','E24','F24','G24','C39','D39','C49')
    if (-not $ProbeOnly) {
    if ($null -eq $resumeData.base) {
        OpenBook $sourceFile
        $initialCalculation = [int]$excelInstance.Calculation
        AssertDrivers $plan.initial.drivers
        $excelInstance.Calculation = -4105
        $excelInstance.CalculateFullRebuild()
        AssertDone
        AssertDrivers $plan.initial.drivers
        $tables = ReadValues $targets
        # Conserver les tables calculées sans les relancer à la réouverture.
        $excelInstance.Calculation = 2
        $excelInstance.CalculateFullRebuild()
        AssertDone
        AssertDrivers $plan.initial.drivers
        $base = ReadValues $baseRefs
        $book.SaveCopyAs([IO.Path]::GetFullPath($OutputPath))
        CloseBook
    } else {
        if ($resumeData.base.version -ne $excelInstance.Version -or
            $resumeData.base.output_sha256 -ne (Hash $OutputPath)) { throw 'Version Excel ou base différente depuis le point de reprise.' }
        $initialCalculation = $resumeData.base.initial_calculation_mode
        $tables = $resumeData.base.tables
        $base = $resumeData.base.base_outputs
    }
    OpenBook $OutputPath
    $excelInstance.Calculation = 2
    AssertDone
    AssertDrivers $plan.initial.drivers
    $persistedTables = ReadValues $targets
    $persistedBase = ReadValues $baseRefs
    CloseBook
    if ((Hash $sourceFile) -ne $plan.source_sha256) { throw 'Source modifiée avant le point de contrôle de base.' }
    $baseProof = @{tables=$tables; persisted_tables=$persistedTables; base_outputs=$base; persisted_base_outputs=$persistedBase;
                   source_sha256=$plan.source_sha256; output_sha256=(Hash $OutputPath); source_preserved=$true;
                   save_reopen_verified=$true; macros_enabled=$false; iteration_enabled=$false; calculation_state=0;
                   restoration='ISOLATION_PAR_COPIES_BASE_JAMAIS_CHOQUEE'; scalar_copies_saved=$false;
                   technical_writes_to_base=@(); version=$excelInstance.Version; initial_calculation_mode=$initialCalculation}
    if ($null -eq $resumeData.base) { Emit @{event='checkpoint'; id='base'; data=$baseProof} }
    Emit @{event='progress'; stage='base_saved_reopened'; elapsed_seconds=([DateTime]::UtcNow-$started).TotalSeconds}
    }
    $observations = @($resumeData.scalars)
    $resumedCount = $observations.Count
    $position = -1
    foreach ($scenario in $plan.scenarios) {
        if ($ProbeOnly -and $scenario.id -notin @('volume_40','volume_44')) { continue }
        $position++
        if ($position -lt $resumedCount) { continue }
        $caseStarted = [DateTime]::UtcNow
        $expectedFile = Join-Path (Split-Path -Parent $PlanPath) ($scenario.id + '.xlsm')
        if ([IO.Path]::GetFullPath($scenario.path) -ne [IO.Path]::GetFullPath($expectedFile) -or
            (Hash $scenario.path) -ne $scenario.sha256) { throw 'Copie scalaire hors campagne ou modifiée.' }
        if ($scenario.id -match '^tornado_[1-9]$') { $refs = @('D24','E24','F24','G24') }
        elseif ($scenario.id -match '^volume_4[0-5]$') { $refs = @('C39','D39') }
        elseif ($scenario.id -match '^matrix_[DEF]5[0-2]$') { $refs = @('C49') }
        else { throw 'Identifiant scalaire non autorisé.' }
        OpenBook $scenario.path
        $excelInstance.Calculation = 2
        AssertDrivers $scenario.drivers
        $excelInstance.CalculateFullRebuild()
        AssertDone
        AssertDrivers $scenario.drivers
        $values = ReadValues $refs
        CloseBook
        $preserved = (Hash $scenario.path) -eq $scenario.sha256
        if (-not $preserved) { throw 'Copie scalaire modifiée sur disque.' }
        $observation = @{id=$scenario.id; sha256=$scenario.sha256; drivers=$scenario.drivers; outputs=$values;
                         calculation_state=0; calculation_mode='AUTO_NO_TABLE'; copy_preserved=$true;
                         elapsed_seconds=([DateTime]::UtcNow-$caseStarted).TotalSeconds}
        $observations += $observation
        Emit @{event='checkpoint'; id=$scenario.id; data=$observation}
        Emit @{event='progress'; stage='scalar_complete'; id=$scenario.id; completed=$observations.Count;
               elapsed_seconds=([DateTime]::UtcNow-$started).TotalSeconds}
    }
    if ((Hash $sourceFile) -ne $plan.source_sha256) { throw 'Source modifiée sur disque.' }
    if ($ProbeOnly) {
        if ($observations.Count -ne 2 -or $observations[0].id -ne 'volume_40' -or $observations[1].id -ne 'volume_44') {
            throw 'La sonde exige les deux scénarios volume attendus exactement une fois.'
        }
        $result = @{schema='tca-sensitivity-probe/1'; application='Microsoft Excel'; version=$excelInstance.Version;
                    source_sha256=$plan.source_sha256; plan_sha256=$PlanSha256; scalars=$observations;
                    source_preserved=$true; macros_enabled=$false; iteration_enabled=$false; calculation_state=0;
                    scalar_calculation_mode='AUTO_NO_TABLE'; scalar_copies_saved=$false; technical_writes_to_base=@();
                    tables_qualified=$false; adopted=$false; physical_sheet=$sheetName;
                    started_at_utc=$started.ToString('o'); completed_at_utc=[DateTime]::UtcNow.ToString('o')}
        if ($null -ne $nativeMapping) {
            $result.profile_sha256 = $nativeMapping.profile_sha256
            $result.native_mapping_sha256 = $nativeMapping.mapping_sha256
        }
        $result | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
        Emit @{event='saved'}
        return
    }
    $result = @{schema='tca-sensitivity-native/1'; application='Microsoft Excel'; version=$excelInstance.Version;
                source_sha256=$plan.source_sha256; output_sha256=(Hash $OutputPath); tables=$tables; persisted_tables=$persistedTables;
                base_outputs=$base; persisted_base_outputs=$persistedBase; scalars=$observations;
                source_preserved=$true; save_reopen_verified=$true; macros_enabled=$false; iteration_enabled=$false;
                calculation_state=0; initial_calculation_mode=$initialCalculation; base_calculation_mode='AUTOMATIC_WITH_TABLES';
                scalar_calculation_mode='AUTO_NO_TABLE'; restoration='ISOLATION_PAR_COPIES_BASE_JAMAIS_CHOQUEE';
                scalar_copies_saved=$false; technical_writes_to_base=@(); adopted=$false;
                started_at_utc=$started.ToString('o'); completed_at_utc=[DateTime]::UtcNow.ToString('o')}
    if ($null -ne $nativeMapping) {
        $result.profile_sha256 = $nativeMapping.profile_sha256
        $result.native_mapping_sha256 = $nativeMapping.mapping_sha256
        $result.physical_sheet = $sheetName
    }
    $result | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
    Emit @{event='saved'}
} catch {
    $originalError = $_.Exception.Message
    # Une copie d'échec n'est jamais une sortie de dossier ni un point de reprise.
    # Elle conserve les caches utiles au diagnostic, sans sauvegarder la source.
    if ($ownedConfirmed -and $null -ne $book) {
        try {
            $diagnosticPath = [IO.Path]::GetFullPath($OutputPath) + '.diagnostic.xlsm'
            if (-not (Test-Path -LiteralPath $diagnosticPath)) {
                $excelInstance.Calculation = -4135
                $book.SaveCopyAs($diagnosticPath)
                Emit @{event='progress'; stage='diagnostic_copy_saved'; file=[IO.Path]::GetFileName($diagnosticPath)}
            }
        } catch { }
    }
    Emit @{event='error'; error=$originalError}
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
