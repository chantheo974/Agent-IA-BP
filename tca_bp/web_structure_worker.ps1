param([Parameter(Mandatory=$true)][string]$RequestPath)
$ErrorActionPreference='Stop'
[Console]::InputEncoding=New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false)
$excel=$null;$book=$null;$owned=$false;$stage='initialisation'
function Emit($value){[Console]::WriteLine(($value|ConvertTo-Json -Depth 10 -Compress));[Console]::Out.Flush()}
function Hash($path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function FormulaKey($value){
    return [regex]::Replace(([string]$value).TrimStart('='),"'([\p{L}_][\p{L}\p{N}_]*)'!",'$1!')
}
function SetCellFormula($cell,$formula){
    $formatRange=$cell
    if($cell.MergeCells){$formatRange=$cell.MergeArea}
    $format=$formatRange.NumberFormat
    try {
        if($format -eq '@'){$formatRange.NumberFormat='0'}
        $cell.Formula2='='+$formula
    } catch {throw ($_.Exception.Message+' [format='+[string]$format+'; protected='+[string]$cell.Parent.ProtectContents+']')} finally {if($format -eq '@'){$formatRange.NumberFormat=$format}}
}
function CellSnapshot($cell){
    $formula=$null
    if($cell.HasFormula){$formula=[string]$cell.Formula2}
    return @{value=$cell.Value2;formula=$formula}
}
function SheetSnapshot($sheet){
    return @{name=[string]$sheet.Name;index=[int]$sheet.Index;
      used_range=[string]$sheet.UsedRange.Address();
      rows=[int]$sheet.UsedRange.Rows.Count;columns=[int]$sheet.UsedRange.Columns.Count}
}
try {
    $request=Get-Content -LiteralPath $RequestPath -Raw -Encoding UTF8|ConvertFrom-Json
    if ((Hash $request.source) -ne $request.source_sha256 -or (Test-Path -LiteralPath $request.output)){throw 'Source périmée ou destination existante.'}
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TcaWebExcelWindow {
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
}
'@
    $previousExcelPids = @(Get-Process -Name EXCEL -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $createdDedicated = $false
    $excel=New-Object -ComObject Excel.Application
    [uint32]$excelPid=0
    [void][TcaWebExcelWindow]::GetWindowThreadProcessId([IntPtr]$excel.Hwnd,[ref]$excelPid)
    $createdDedicated = $excelPid -gt 0 -and ($previousExcelPids -notcontains [int]$excelPid)
    if (-not $createdDedicated) { throw 'Instance Excel existante : aucun droit de fermeture.' }
    Emit @{event='owned_process';pid=$excelPid}
    $ack=[Console]::ReadLine()|ConvertFrom-Json
    if ($ack.operation -ne 'ownership_confirmed'){throw 'Instance dédiée non confirmée.'}
    $owned=$true
    if ($excel.Workbooks.Count -ne 0){throw 'Instance Excel non vide.'}
    $excel.Visible=$false;$excel.DisplayAlerts=$false;$excel.EnableEvents=$false
    $excel.AutomationSecurity=3;$excel.AskToUpdateLinks=$false
    $book=$excel.Workbooks.Open($request.source,0,$true)
    if (-not $book.ReadOnly -or $excel.Iteration){throw 'État du classeur incompatible.'}
    $excel.Calculation=-4135
    $bookProtection=@{structure=[bool]$book.ProtectStructure;windows=[bool]$book.ProtectWindows}
    $book.Unprotect()
    $protections=@{}
    foreach($sheet in $book.Worksheets){
        if($sheet.Protection.AllowEditRanges.Count -gt 0){throw 'Une autorisation de plage protégée nécessite une adaptation explicite.'}
        $p=$sheet.Protection
        $protections[$sheet.CodeName]=@{contents=[bool]$sheet.ProtectContents;drawing=[bool]$sheet.ProtectDrawingObjects;scenarios=[bool]$sheet.ProtectScenarios;
          formatCells=[bool]$p.AllowFormattingCells;formatColumns=[bool]$p.AllowFormattingColumns;formatRows=[bool]$p.AllowFormattingRows;
          insertColumns=[bool]$p.AllowInsertingColumns;insertRows=[bool]$p.AllowInsertingRows;insertLinks=[bool]$p.AllowInsertingHyperlinks;
          deleteColumns=[bool]$p.AllowDeletingColumns;deleteRows=[bool]$p.AllowDeletingRows;sorting=[bool]$p.AllowSorting;
          filtering=[bool]$p.AllowFiltering;pivot=[bool]$p.AllowUsingPivotTables;selection=[int]$sheet.EnableSelection}
        $sheet.Unprotect()
        if($sheet.ProtectContents -or $sheet.ProtectDrawingObjects -or $sheet.ProtectScenarios){throw 'Protection de feuille non reproductible sans mot de passe.'}
    }
    if($book.ProtectStructure -or $book.ProtectWindows){throw 'Protection du classeur non reproductible sans mot de passe.'}
    $repairGroups=$request.reference_repair_groups
    if($null -eq $repairGroups){
        $repairGroups=@()
        for($i=0;$i -lt @($request.reference_repairs).Count;$i++){$repairGroups+=,@($i)}
    }
    foreach($indices in $repairGroups){
        $batch=@(foreach($i in $indices){$request.reference_repairs[[int]$i]})
        if($batch.Count -eq 0){continue}
        $first=$batch[0];$last=$batch[$batch.Count-1]
        $stage='references '+$first.sheet+'!'+$first.cell+':'+$last.cell
        $range=$book.Worksheets.Item($first.sheet).Range($first.cell+':'+$last.cell)
        if($range.HasFormula -ne $true){throw 'La plage de references contient une cellule sans formule.'}
        $original=$range.Formula2
        $matrix=[Array]::CreateInstance([object],[int[]]@(1,$batch.Count),[int[]]@(1,1))
        for($i=0;$i -lt $batch.Count;$i++){
            $seen=if($batch.Count -eq 1){$original}else{$original.GetValue(1,$i+1)}
            if((FormulaKey $seen) -ne (FormulaKey $batch[$i].before)){throw 'Formule de reference positionnelle perimee.'}
            $matrix.SetValue('='+$batch[$i].after,1,$i+1)
        }
        if($batch.Count -eq 1){SetCellFormula $range $first.after}
        else {
            $range.Formula2=$matrix
            if($range.HasFormula -ne $true){
                foreach($repair in $batch){SetCellFormula ($book.Worksheets.Item($repair.sheet).Range($repair.cell)) $repair.after}
            }
        }
        $written=$range.Formula2
        if($range.HasFormula -ne $true){throw 'La reparation des references doit persister des formules.'}
        for($i=0;$i -lt $batch.Count;$i++){
            $seen=if($batch.Count -eq 1){$written}else{$written.GetValue(1,$i+1)}
            if((FormulaKey $seen) -ne (FormulaKey $batch[$i].after)){throw ('Reference positionnelle non persistee : '+$batch[$i].sheet+'!'+$batch[$i].cell)}
        }
    }
    $changes=New-Object System.Collections.Generic.List[object]
    foreach($operation in $request.operations){
        $kind=$operation.type
        $stage=$kind+' '+$operation.sheet+'!'+$operation.cell
        $before=$null;$after=$null
        if($kind -eq 'add_sheet'){
            $sheet=$book.Worksheets.Add([Type]::Missing,$book.Worksheets.Item($book.Worksheets.Count))
            $sheet.Name=$operation.name
        } else {
            $sheet=$book.Worksheets.Item($operation.sheet)
            if($kind -eq 'set_value' -or $kind -eq 'set_formula'){$before=CellSnapshot $sheet.Range($operation.cell)}
            else{$before=SheetSnapshot $sheet}
            switch($kind){
                {$_ -in @('extend_register','extend_offer')} {
                    foreach($step in $operation.geometry){
                        $stage='insertion '+$step.sheet+'!'+[string]$step.index
                        $targetSheet=$book.Worksheets.Item($step.sheet)
                        $targetSheet.Rows.Item([string]$step.index+':'+[string]($step.index+$step.count-1)).Insert()|Out-Null
                    }
                    foreach($block in $operation.clones){
                        $stage='copie '+$block.sheet+'!'+[string]$block.source_first+':'+[string]$block.source_last
                        $targetSheet=$book.Worksheets.Item($block.sheet)
                        $from=$targetSheet.Range($targetSheet.Cells.Item($block.source_first,1),$targetSheet.Cells.Item($block.source_last,$block.last_column))
                        $to=$targetSheet.Range($targetSheet.Cells.Item($block.destination_first,1),$targetSheet.Cells.Item($block.destination_last,$block.last_column))
                        $from.Copy($to)|Out-Null
                    }
                    foreach($entry in $operation.cells){
                        $stage='ecriture '+$entry.sheet+'!'+$entry.cell
                        $cell=$book.Worksheets.Item($entry.sheet).Range($entry.cell)
                        if($entry.PSObject.Properties.Name -contains 'formula'){SetCellFormula $cell $entry.formula}
                        elseif($null -eq $entry.value){if($cell.MergeCells){$cell.MergeArea.ClearContents()}else{$cell.ClearContents()}}
                        elseif($entry.value -is [string]){$cell.Value2="'"+$entry.value}
                        elseif($entry.value -is [bool]){$cell.Value2=[bool]$entry.value}
                        else{$cell.Value2=[double]$entry.value}
                    }
                }
                'set_value' {
                    $cell=$sheet.Range($operation.cell)
                    if($null -eq $operation.value){$cell.ClearContents()}
                    elseif($operation.value -is [string]){$cell.Value2="'"+$operation.value}
                    elseif($operation.value -is [bool]){$cell.Value2=[bool]$operation.value}
                    else{$cell.Value2=[double]$operation.value}
                }
                'set_formula' {SetCellFormula ($sheet.Range($operation.cell)) $operation.formula}
                'insert_rows' {$sheet.Rows.Item([string]$operation.index+':'+[string]($operation.index+$operation.count-1)).Insert()|Out-Null}
                'delete_rows' {$sheet.Rows.Item([string]$operation.index+':'+[string]($operation.index+$operation.count-1)).Delete()|Out-Null}
                'insert_columns' {$sheet.Range($sheet.Cells.Item(1,$operation.index),$sheet.Cells.Item(1,$operation.index+$operation.count-1)).EntireColumn.Insert()|Out-Null}
                'delete_columns' {$sheet.Range($sheet.Cells.Item(1,$operation.index),$sheet.Cells.Item(1,$operation.index+$operation.count-1)).EntireColumn.Delete()|Out-Null}
                'rename_sheet' {$sheet.Name=$operation.name}
                'delete_sheet' {$sheet.Delete()}
                'move_sheet' {
                    $index=[int]$operation.index
                    if($sheet.Index -gt $index){$sheet.Move($book.Worksheets.Item($index))}
                    elseif($sheet.Index -lt $index){$sheet.Move([Type]::Missing,$book.Worksheets.Item($index))}
                }
                default {throw 'Opération inconnue.'}
            }
        }
        if($kind -eq 'set_value' -or $kind -eq 'set_formula'){$after=CellSnapshot $sheet.Range($operation.cell)}
        elseif($kind -ne 'delete_sheet'){$after=SheetSnapshot $sheet}
        $change=@{type=$kind;sheet=$operation.sheet;cell=$operation.cell;before=$before;after=$after;operation_index=$changes.Count}
        foreach($key in @('name','index','count','role','evidence_id','reason')){if($operation.PSObject.Properties.Name -contains $key){$change[$key]=$operation.$key}}
        $changes.Add($change)
        Emit @{event='progress';operation=$kind}
    }
    foreach($sheet in $book.Worksheets){
        $p=$protections[$sheet.CodeName]
        if($p -and ($p.contents -or $p.drawing -or $p.scenarios)){
            $sheet.Protect([Type]::Missing,$p.drawing,$p.contents,$p.scenarios,$false,
              $p.formatCells,$p.formatColumns,$p.formatRows,$p.insertColumns,$p.insertRows,$p.insertLinks,
              $p.deleteColumns,$p.deleteRows,$p.sorting,$p.filtering,$p.pivot)
            $sheet.EnableSelection=$p.selection
        }
    }
    if($bookProtection.structure -or $bookProtection.windows){$book.Protect([Type]::Missing,$bookProtection.structure,$bookProtection.windows)}
    $book.ForceFullCalculation=$true
    $book.SaveCopyAs([IO.Path]::GetFullPath($request.output))
    $book.Close($false);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book);$book=$null
    $saved=Hash $request.output
    $book=$excel.Workbooks.Open($request.output,0,$true)
    if(-not $book.ReadOnly -or $excel.AutomationSecurity -ne 3 -or $excel.EnableEvents){throw 'Réouverture non conforme.'}
    $book.Close($false);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book);$book=$null
    if((Hash $request.source) -ne $request.source_sha256 -or (Hash $request.output) -ne $saved){throw 'Classeur modifié pendant vérification.'}
    @{status='MODIFIE_RECALCUL_NON_CERTIFIE';source_sha256=$request.source_sha256;output_sha256=$saved;
      macros_enabled=$false;events_enabled=$false;links_updated=$false;save_reopen_verified=$true;
      source_preserved=$true;owned_excel_pid=$excelPid;financial_outputs_verified=$false;adopted=$false;
      protection_options_restored=$true;changes=$changes.ToArray();reference_repairs=@($request.reference_repairs)}|
      ConvertTo-Json -Depth 10|Set-Content -LiteralPath $request.receipt -Encoding UTF8
    Emit @{event='saved'}
} catch {Emit @{event='error';error=($_.Exception.Message+' ['+$stage+']')};exit 2}
finally {
    try {
        if($book){try{$book.Close($false)}finally{[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book)}}
    } finally {
        if($excel){try{if($owned -or $createdDedicated){$excel.Quit()}}finally{[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)}}
        [GC]::Collect();[GC]::WaitForPendingFinalizers()
    }
}
