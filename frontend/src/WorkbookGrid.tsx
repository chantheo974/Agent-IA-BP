import { useCallback, useEffect, useMemo, useRef, useState, type ClipboardEvent } from "react";
import DataEditor, { CompactSelection, GridCellKind, type DataEditorRef, type GridCell, type GridColumn, type GridSelection, type Item, type Rectangle } from "@glideapps/glide-data-grid";
import { api, casePath, columnName, displayValue, errorText, parseAddress, parseValue, type NumericLocale } from "./api";
import type { Cell, Draft, Operation, Scope, Sheet } from "./types";
import { Button, Icon, Modal, PageNavigation } from "./ui";

const emptySelection = (): GridSelection => ({ columns: CompactSelection.empty(), rows: CompactSelection.empty() });
function operation(sheet: string, cell: string, raw: string, locale?: NumericLocale): Operation {
  return raw.startsWith("=") ? { type: "set_formula", sheet, cell, formula: raw } : { type: "set_value", sheet, cell, value: parseValue(raw, locale) };
}

export default function WorkbookGrid({ caseId, sheet, draft, refresh, disabled, focusCell, onEdit, onScope, onStructural, onDiscuss, ordinary = false, revision }: {
  caseId: string; sheet: Sheet; draft: Draft; refresh: number; disabled: boolean;
  focusCell?: string; onDiscuss?: () => void; ordinary?: boolean; revision?: number;
  onEdit: (operations: Operation[], scope: Scope, expectedRevision?: number) => Promise<void>;
  onScope: (scope: Scope) => void;
  onStructural: (kind: string, index: number) => void;
}) {
  const rootRef = useRef<HTMLDivElement>(null), editorRef = useRef<DataEditorRef>(null);
  const cache = useRef(new Map<string, Cell & { readRevision?: number }>()), loaded = useRef(new Set<string>()), pending = useRef(new Set<string>()), generation = useRef(0);
  const [cacheVersion, setCacheVersion] = useState(0), [size, setSize] = useState({ width: 600, height: 400 });
  const [selection, setSelection] = useState<GridSelection>(emptySelection), [address, setAddress] = useState("A1"), [formula, setFormula] = useState("");
  const [loadError, setLoadError] = useState(""), [showSearch, setShowSearch] = useState(false), [loading, setLoading] = useState(0);
  const [localError, setLocalError] = useState("");
  const [numericLocale, setNumericLocale] = useState<NumericLocale>("fr");
  const [paste, setPaste] = useState<{ target: Item; values: readonly (readonly string[])[]; revision?: number } | null>(null);
  const [pastePage, setPastePage] = useState(0);
  const pasteCells = useMemo(() => paste?.values.flatMap((row, r) => row.map((raw, c) => ({ raw, r, c }))) || [], [paste]);
  const formulaDirty = useRef(false), editingAddress = useRef("A1");
  const editRevision = useRef<number | undefined>(undefined);
  const overlayEdit = useRef<{ cell: string; revision?: number } | null>(null);
  const region = useRef<Rectangle>({ x: 0, y: 0, width: 26, height: 60 });
  const rowCount = Math.max(1, Math.min(1048576, sheet.rows || 1000));
  const columnCount = Math.max(1, Math.min(16384, sheet.columns || 26));
  const overlay = useMemo(() => {
    const map = new Map<string, Operation>();
    for (const op of draft.operations || []) if (op.sheet === sheet.name && op.cell && ["set_value", "set_formula"].includes(op.type)) map.set(op.cell.toUpperCase(), op);
    return map;
  }, [draft.operations, sheet.name]);
  const loadRegion = useCallback(async (rectangle: Rectangle) => {
    const ownGeneration = generation.current;
    const requests: Promise<void>[] = [];
    const startRow = Math.floor(Math.max(0, rectangle.y - 15) / 100) * 100, lastRow = Math.min(rowCount - 1, rectangle.y + rectangle.height + 15);
    const startCol = Math.floor(Math.max(0, rectangle.x - 2) / 26) * 26, lastCol = Math.min(columnCount - 1, rectangle.x + rectangle.width + 2);
    for (let row = startRow; row <= lastRow; row += 100) for (let col = startCol; col <= lastCol; col += 26) {
      const key = row + ":" + col;
      if (loaded.current.has(key)) { loaded.current.delete(key); loaded.current.add(key); continue; }
      if (pending.current.has(key)) continue;
      pending.current.add(key); setLoading(n => n + 1);
      const rows = Math.min(100, rowCount - row), columns = Math.min(26, columnCount - col);
      const query = new URLSearchParams({ sheet: sheet.name, row: String(row + 1), column: String(col + 1), rows: String(rows), columns: String(columns) });
      requests.push(api<{ cells: Cell[]; revision: number }>(casePath(caseId) + (ordinary ? "/cockpit/cells?" : "/cells?") + query).then(result => {
        if (generation.current !== ownGeneration) return;
        for (let r = row; r < row + rows; r++) for (let c = col; c < col + columns; c++) {
          const cell = columnName(c + 1) + (r + 1);
          cache.current.set(cell, { cell, row: r + 1, column: c + 1, value: null, readRevision: result.revision });
        }
        for (const cell of result.cells) cache.current.set(cell.cell.toUpperCase(), { ...cell, readRevision: result.revision });
        loaded.current.add(key);
        while (loaded.current.size > 8) {
          const oldest = loaded.current.values().next().value!;
          loaded.current.delete(oldest);
          const [oldRow, oldCol] = oldest.split(":").map(Number);
          for (let r = oldRow; r < Math.min(rowCount, oldRow + 100); r++) for (let c = oldCol; c < Math.min(columnCount, oldCol + 26); c++) cache.current.delete(columnName(c + 1) + (r + 1));
        }
        setLoadError(""); setCacheVersion(n => n + 1);
      }).catch(error => { if (generation.current === ownGeneration) setLoadError(errorText(error)); }).finally(() => {
        if (generation.current === ownGeneration) { pending.current.delete(key); setLoading(n => Math.max(0, n - 1)); }
      }));
    }
    await Promise.all(requests);
  }, [caseId, sheet.name, rowCount, columnCount, ordinary]);
  useEffect(() => {
    generation.current++; cache.current.clear(); loaded.current.clear(); pending.current.clear(); setLoading(0); setCacheVersion(n => n + 1);
    setLoadError(""); void loadRegion(region.current);
  }, [caseId, sheet.name, refresh, loadRegion]);
  useEffect(() => {
    setSelection(emptySelection()); setAddress("A1"); setFormula(""); setLocalError("");
    region.current = { x: 0, y: 0, width: 26, height: 60 };
    onScope({ sheet: sheet.name, range: "A1" });
  }, [sheet.name, caseId]);
  useEffect(() => {
    const node = rootRef.current;
    if (!node) return;
    const observer = new ResizeObserver(entries => { const rect = entries[0].contentRect; setSize({ width: Math.max(100, rect.width), height: Math.max(100, rect.height) }); });
    observer.observe(node); return () => observer.disconnect();
  }, []);
  const currentCell = selection.current?.cell || [0, 0];
  const currentAddress = columnName(currentCell[0] + 1) + (currentCell[1] + 1);
  const current = cache.current.get(currentAddress), proposed = overlay.get(currentAddress);
  const currentProtected = ordinary && current?.editable !== true;
  const currentRaw = proposed ? proposed.type === "set_formula" ? proposed.formula || "" : displayValue(proposed.value) : current?.formula ? (current.formula.startsWith("=") ? current.formula : "=" + current.formula) : displayValue(current?.value);
  useEffect(() => {
    if (editingAddress.current !== currentAddress) { editingAddress.current = currentAddress; formulaDirty.current = false; editRevision.current = undefined; }
    if (!formulaDirty.current) setFormula(currentRaw);
  }, [currentAddress, currentRaw]);
  const columns = useMemo<readonly GridColumn[]>(() => Array.from({ length: columnCount }, (_, index) => ({ title: columnName(index + 1), id: String(index), width: index === 0 ? 176 : 132 })), [columnCount]);
  const [widths, setWidths] = useState<Record<number, number>>({});
  const sizedColumns = useMemo(() => columns.map((column, index) => ({ ...column, width: widths[index] || ("width" in column ? column.width : 132) })), [columns, widths]);
  const formatCell = useCallback(([col, row]: Item, value?: Cell): GridCell => {
    const addr = columnName(col + 1) + (row + 1), change = overlay.get(addr);
    if (!value && !change) return { kind: GridCellKind.Loading, allowOverlay: false };
    const raw = change ? change.type === "set_formula" ? change.formula || "" : displayValue(change.value) : value?.formula ? (value.formula.startsWith("=") ? value.formula : "=" + value.formula) : displayValue(value?.value);
    const display = change ? raw : value?.display ?? displayValue(value?.value);
    return { kind: GridCellKind.Text, data: raw, displayData: display, allowOverlay: true, readonly: disabled || (ordinary && value?.editable !== true),
      themeOverride: change ? { bgCell: "#fff3da", textDark: "#7c5015" } : value?.formula ? { textDark: "#28625b" } : undefined,
      contentAlign: typeof value?.value === "number" && !change ? "right" : "left" };
  }, [overlay, disabled, ordinary]);
  const getCell = useCallback((item: Item) => formatCell(item, cache.current.get(columnName(item[0] + 1) + (item[1] + 1))), [cacheVersion, formatCell]);
  async function copyCells(rectangle: Rectangle): Promise<GridCell[][]> {
    if (rectangle.width * rectangle.height > 20000) { setLocalError("Limitez la copie à 20 000 cellules. Aucune lecture supplémentaire n’a été lancée."); return []; }
    const ownGeneration = generation.current, values = new Map<string, Cell>();
    const windows: Rectangle[] = [];
    for (let col = rectangle.x; col < rectangle.x + rectangle.width; col += 100) {
      const width = Math.min(100, rectangle.x + rectangle.width - col), height = Math.min(500, Math.floor(20000 / width));
      for (let row = rectangle.y; row < rectangle.y + rectangle.height; row += height) windows.push({ x: col, y: row, width, height: Math.min(height, rectangle.y + rectangle.height - row) });
    }
    try {
      for (let index = 0; index < windows.length; index += 4) {
        await Promise.all(windows.slice(index, index + 4).map(async window => {
          const query = new URLSearchParams({ sheet: sheet.name, row: String(window.y + 1), column: String(window.x + 1), rows: String(window.height), columns: String(window.width) });
          const result = await api<{ cells: Cell[] }>(casePath(caseId) + (ordinary ? "/cockpit/cells?" : "/cells?") + query);
          for (const cell of result.cells) values.set(cell.cell.toUpperCase(), cell);
        }));
        if (ownGeneration !== generation.current) { setLocalError("Le dossier a changé pendant la copie. Sélectionnez à nouveau les cellules."); return []; }
      }
      setLocalError("");
      return Array.from({ length: rectangle.height }, (_, r) => Array.from({ length: rectangle.width }, (_, c) => { const col = rectangle.x + c, row = rectangle.y + r, cell = columnName(col + 1) + (row + 1); return formatCell([col, row], values.get(cell) || { cell, row: row + 1, column: col + 1, value: null }); }));
    } catch (error) { setLocalError(errorText(error)); return []; }
  }
  function copySelection(event: ClipboardEvent<HTMLDivElement>) {
    event.preventDefault(); event.stopPropagation();
    const ownGeneration = generation.current;
    const rowIndices = selection.rows.toArray(), colIndices = selection.columns.toArray();
    const count = selection.current ? selection.current.range.width * selection.current.range.height : rowIndices.length ? rowIndices.length * columnCount : colIndices.length * rowCount;
    if (count > 20000) { setLocalError("Limitez la copie à 20 000 cellules. Aucune lecture supplémentaire n’a été lancée."); return; }
    if (!count) return;
    const group = (indices: number[]) => indices.reduce<{ start: number; count: number }[]>((groups, index) => { const last = groups.at(-1); if (last && index === last.start + last.count) last.count++; else groups.push({ start: index, count: 1 }); return groups; }, []);
    const rectangles: Rectangle[] = selection.current ? [selection.current.range] : rowIndices.length ? group(rowIndices).map(({ start, count }) => ({ x: 0, y: start, width: columnCount, height: count })) : group(colIndices).map(({ start, count }) => ({ x: start, y: 0, width: count, height: rowCount }));
    void (async () => {
      let cells: GridCell[][] = [];
      for (const rectangle of rectangles) {
        const next = await copyCells(rectangle); if (!next.length) return;
        if (generation.current !== ownGeneration) { setLocalError("Le dossier a changé pendant la copie. Sélectionnez à nouveau les cellules."); return; }
        cells = !selection.current && !rowIndices.length && cells.length ? cells.map((row, index) => [...row, ...next[index]]) : [...cells, ...next];
      }
      const escaped = (cell: GridCell) => { const value = cell.kind === GridCellKind.Text ? cell.data : ""; return /[\t\n\r"]/.test(value) ? '"' + value.replaceAll('"', '""') + '"' : value; };
      try { await navigator.clipboard.writeText(cells.map(row => row.map(escaped).join("\t")).join("\n")); }
      catch { setLocalError("Le navigateur n’a pas autorisé la copie. Autorisez son accès au presse-papiers puis réessayez."); }
    })();
  }
  const select = useCallback((next: GridSelection) => {
    setSelection(next);
    if (!next.current) return;
    const { cell: [col, row], range } = next.current;
    setAddress(columnName(col + 1) + (row + 1));
    const a = columnName(range.x + 1) + (range.y + 1), b = columnName(range.x + range.width) + (range.y + range.height);
    onScope({ sheet: sheet.name, range: a === b ? a : a + ":" + b });
  }, [onScope, sheet.name]);
  async function submit(operations: Operation[], scope: Scope, expectedRevision?: number) {
    setLocalError("");
    if (ordinary && (expectedRevision === undefined || expectedRevision !== revision)) {
      setLocalError('Le dossier a changé depuis le début de cette saisie. Votre texte est conservé : relisez la nouvelle révision avant de préparer un nouveau lot.');
      return false;
    }
    if (ordinary && operations.some(op => op.type !== 'set_value')) {
      setLocalError('Les formules sont protégées dans le cockpit. Saisissez une valeur dans une entrée métier autorisée.');
      return false;
    }
    try { await onEdit(operations, scope, ordinary ? expectedRevision : undefined); return true; } catch (error) { setLocalError(errorText(error)); return false; }
  }
  async function saveFormula() {
    const target = currentAddress, change = operation(sheet.name, target, formula);
    const accepted = await submit([change], { sheet: sheet.name, range: target }, ordinary ? editRevision.current ?? current?.readRevision : undefined);
    if (accepted && editingAddress.current === target) { formulaDirty.current = false; setFormula(change.type === "set_formula" ? change.formula || "" : displayValue(change.value)); }
  }
  function navigate() {
    const parsed = parseAddress(address);
    if (!parsed || parsed[0] >= columnCount || parsed[1] >= rowCount) { setLocalError("Cette adresse ne fait pas partie de la feuille. Ajoutez les lignes ou colonnes nécessaires."); return; }
    const [col, row] = parsed;
    setLocalError("");
    select({ ...emptySelection(), current: { cell: parsed, range: { x: col, y: row, width: 1, height: 1 }, rangeStack: [] } });
    editorRef.current?.scrollTo(col, row, "both", 0, 0, { hAlign: "center", vAlign: "center" });
    void loadRegion({ x: col, y: row, width: 8, height: 20 });
  }
  useEffect(() => {
    if (!focusCell) return;
    const parsed = parseAddress(focusCell);
    if (!parsed || parsed[0] >= columnCount || parsed[1] >= rowCount) return;
    const [col, row] = parsed;
    select({ ...emptySelection(), current: { cell: parsed, range: { x: col, y: row, width: 1, height: 1 }, rangeStack: [] } });
    editorRef.current?.scrollTo(col, row, "both", 0, 0, { hAlign: "center", vAlign: "center" });
    void loadRegion({ x: col, y: row, width: 8, height: 20 });
  }, [focusCell, caseId, sheet.name, columnCount, rowCount, select, loadRegion]);
  return <div className="workbook">
    <div className="sheet-toolbar"><div className="sheet-name"><Icon name="table"/><strong>{sheet.name}</strong><span>{rowCount.toLocaleString("fr-FR")} lignes · {columnCount} colonnes</span></div><div className="toolbar-actions">
      {onDiscuss && <button className="icon-button" aria-label="Discuter de cette sélection" title="Discuter de cette sélection" onClick={onDiscuss}><Icon name="chat"/></button>}
      <button className="icon-button" aria-label="Rechercher dans la feuille" title="Rechercher dans la feuille" onClick={() => setShowSearch(true)}><Icon name="search"/></button>
      {!ordinary && <details className="structure-menu"><summary className="icon-button" aria-label="Modifier la structure" title="Modifier la structure"><Icon name="more"/></summary><div className="dropdown">
        <button disabled={disabled} onClick={() => onStructural("insert_rows", currentCell[1] + 1)}>Insérer une ligne avant {currentCell[1] + 1}</button>
        <button disabled={disabled} onClick={() => onStructural("delete_rows", currentCell[1] + 1)}>Supprimer la ligne {currentCell[1] + 1}</button>
        <button disabled={disabled} onClick={() => onStructural("insert_columns", currentCell[0] + 1)}>Insérer une colonne avant {columnName(currentCell[0] + 1)}</button>
        <button disabled={disabled} onClick={() => onStructural("delete_columns", currentCell[0] + 1)}>Supprimer la colonne {columnName(currentCell[0] + 1)}</button>
        <hr/><button disabled={disabled} onClick={() => onStructural("rename_sheet", 0)}>Renommer la feuille</button>
        <button disabled={disabled} onClick={() => onStructural("move_sheet", 0)}>Déplacer la feuille</button>
        <button disabled={disabled} className="danger-text" onClick={() => onStructural("delete_sheet", 0)}>Supprimer la feuille</button>
      </div></details>}
    </div></div>
    <div className="formula-bar"><form onSubmit={event => { event.preventDefault(); navigate(); }}><input aria-label="Adresse de cellule" value={address} onChange={event => setAddress(event.target.value.toUpperCase())}/></form><span className="formula-symbol">ƒx</span><form className="formula-input" onSubmit={event => { event.preventDefault(); void saveFormula(); }}><input aria-label="Valeur ou formule de la cellule" value={formula} disabled={disabled || currentProtected} onChange={event => { if (!formulaDirty.current) editRevision.current = current?.readRevision; formulaDirty.current = true; setFormula(event.target.value); }} placeholder="Valeur ou formule…"/><button type="submit" className="icon-button" title="Ajouter au brouillon" aria-label="Ajouter la valeur au brouillon" disabled={disabled || currentProtected}><Icon name="check"/></button></form></div>
    {ordinary && <p className="grid-permission-note" role="status">{currentProtected ? 'Cellule protégée : résultat, formule ou contenu hors des entrées métier.' : 'Entrée métier autorisée : votre saisie sera ajoutée au brouillon.'}</p>}
    {ordinary && formulaDirty.current && editRevision.current !== revision && <div className="grid-permission-note"><p>Cette saisie a commencé sur une ancienne révision et reste conservée pour comparaison.</p><Button onClick={() => { formulaDirty.current = false; editRevision.current = undefined; setFormula(currentRaw); setLocalError(''); }}>Abandonner cette saisie et relire la cellule</Button></div>}
    {(loadError || localError) && <div className="inline-error" role="alert">{localError || loadError}{loadError && <button onClick={() => void loadRegion(region.current)}>Réessayer</button>}</div>}
    <div className="grid-frame" ref={rootRef} aria-label={"Tableur " + sheet.name} onCopyCapture={copySelection}>
      <DataEditor ref={editorRef} width={size.width} height={size.height} columns={sizedColumns} rows={rowCount} getCellContent={getCell}
        gridSelection={selection} onGridSelectionChange={select} rowMarkers="both" rowMarkerWidth={46} rowHeight={ordinary ? 36 : 30} headerHeight={ordinary ? 40 : 35}
        smoothScrollX smoothScrollY freezeColumns={1} showSearch={showSearch} onSearchClose={() => setShowSearch(false)}
        onColumnResize={(_, width, index) => setWidths(previous => ({ ...previous, [index]: width }))}
        onVisibleRegionChanged={rectangle => { region.current = rectangle; void loadRegion(rectangle); }}
        getCellsForSelection={rectangle => async () => copyCells(rectangle)}
        onCellActivated={location => { const cell = columnName(location[0] + 1) + (location[1] + 1); overlayEdit.current = { cell, revision: cache.current.get(cell)?.readRevision }; }}
        onCellEdited={(location, value) => { if (value.kind !== GridCellKind.Text || disabled) return; const addr = columnName(location[0] + 1) + (location[1] + 1); void submit([operation(sheet.name, addr, value.data)], { sheet: sheet.name, range: addr }, ordinary ? (overlayEdit.current?.cell === addr ? overlayEdit.current.revision : cache.current.get(addr)?.readRevision) : undefined); }}
        onPaste={(target, values) => { if (disabled) return false; if (values.reduce((n, row) => n + row.length, 0) > 2000) { setLocalError("Le collage est limité à 2 000 cellules par lot."); return false; } setPastePage(0); setPaste({ target, values, revision: cache.current.get(columnName(target[0] + 1) + (target[1] + 1))?.readRevision }); return false; }}
        onDelete={next => { if (disabled || !next.current) return false; const rect = next.current.range; if (rect.width * rect.height > 2000) { setLocalError("Limitez l’effacement à 2 000 cellules par lot."); return false; } const operations = Array.from({ length: rect.height }, (_, r) => Array.from({ length: rect.width }, (_, c) => ({ type: "set_value", sheet: sheet.name, cell: columnName(rect.x + c + 1) + (rect.y + r + 1), value: null } as Operation))).flat(); void submit(operations, { sheet: sheet.name, range: columnName(rect.x + 1) + (rect.y + 1) + ":" + columnName(rect.x + rect.width) + (rect.y + rect.height) }, ordinary ? cache.current.get(columnName(rect.x + 1) + (rect.y + 1))?.readRevision : undefined); return false; }}
        theme={{ accentColor: "#267061", accentLight: "#e8f3ef", textDark: "#263e37", textMedium: "#6a7e76", bgHeader: "#f2f5f2", bgHeaderHovered: "#e5eee8", bgHeaderHasFocus: "#dbece3", borderColor: "#e4eae4", horizontalBorderColor: "#e8ece7", fontFamily: "Inter, Segoe UI, sans-serif", baseFontStyle: ordinary ? "16px" : "13px", headerFontStyle: ordinary ? "600 14px" : "600 12px", cellHorizontalPadding: 12 }}
      />
    </div>
    <div className="sheet-status"><span>{loading ? "Chargement des cellules…" : "Prêt"}</span><span>{currentAddress}{current?.format ? " · " + current.format : ""}{proposed ? " · Modification au brouillon" : current?.state ? " · " + current.state : ""}</span><span>Ctrl+C / Ctrl+V · Double-clic pour saisir</span></div>
    {paste && <Modal title="Vérifier le collage" wide onClose={() => setPaste(null)}>{localError && <p role="alert" className="inline-error">{localError}</p>}<label className="form-stack">Format des nombres collés<select aria-label="Format des nombres collés" value={numericLocale} onChange={e => setNumericLocale(e.target.value as NumericLocale)}><option value="fr">Français : 1 234,56</option><option value="en">Anglais : 1,234.56</option></select></label><p className="note">Vérifiez les conversions. Les textes et les identifiants avec un zéro initial sont conservés.</p><PageNavigation count={pasteCells.length} page={pastePage} onPage={setPastePage} label="cellules collées"/><div className="draft-table-wrap"><table className="plain-table"><thead><tr><th>Cellule</th><th>Texte collé</th><th>Proposition</th><th>Type</th></tr></thead><tbody>{pasteCells.slice(pastePage * 200, (pastePage + 1) * 200).map(({ raw, r, c }) => { const cell = columnName(paste.target[0] + c + 1) + (paste.target[1] + r + 1), op = operation(sheet.name, cell, raw, numericLocale); return <tr key={cell}><td>{cell}</td><td>{raw}</td><td>{displayValue(op.formula || op.value)}</td><td>{op.formula ? "Formule" : typeof op.value === "number" ? "Nombre" : op.value === null ? "Vide" : "Texte / valeur"}</td></tr>; })}</tbody></table></div><div className="modal-footer"><Button onClick={() => setPaste(null)}>Annuler</Button><Button className="primary" disabled={disabled} onClick={() => { const { target, values } = paste; const operations = values.flatMap((row, r) => row.map((value, c) => operation(sheet.name, columnName(target[0] + c + 1) + (target[1] + r + 1), value, numericLocale))); const first = columnName(target[0] + 1) + (target[1] + 1), last = columnName(target[0] + Math.max(...values.map(row => row.length))) + (target[1] + values.length); void submit(operations, { sheet: sheet.name, range: first + ":" + last }, ordinary ? paste.revision : undefined).then(ok => { if (ok) setPaste(null); }); }}>Ajouter le collage au brouillon</Button></div></Modal>}
  </div>;
}
