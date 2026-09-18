import { useState } from 'react';
import { useRouter } from '../cockpit/router';
import { Button } from '@/components/ui/button';
import { StateBadge, Surface } from '@/components/cockpit/page-elements';
import { statusLabel } from '../api';
import type { Catalog, CatalogSheet, ConnectedProps } from './types';
import { textValue, useCaseData } from './data';

type Provenance = { case_id: string; revision: number; sha256: string };
type CellSource = { sheet: string; cell: string };
type Qualification = {
  scenario_ready?: boolean;
  blockers?: { message?: string }[];
  hypotheses?: { message?: string }[];
};
type OutputBase = {
  id: string; label: string; unit?: string; status: string; available: boolean;
  provenance: Provenance; qualification?: Qualification;
};
type OutputMetric = OutputBase & {
  value: number | string | null; period?: string; metric?: string;
  sheet?: string; cell?: string; sources?: CellSource[];
};
type OutputSeries = OutputBase & {
  categories: string[]; values: (number | null)[]; sources: CellSource[];
  case_id: string; revision: number;
};
export type SheetOutputSnapshot = Provenance & {
  schema: 'tca-cockpit-outputs/1'; profile_sha256: string; calculation_status: string;
  outputs_current: boolean; sheet_id: string; series: OutputSeries[];
  metrics: OutputMetric[]; annual_metrics: OutputMetric[]; diagnostics: string[];
};

function sameProvenance(item: OutputBase, snapshot: SheetOutputSnapshot) {
  return item.provenance?.case_id === snapshot.case_id && item.provenance?.revision === snapshot.revision && item.provenance?.sha256 === snapshot.sha256;
}
function available(item: OutputBase, snapshot: SheetOutputSnapshot) {
  return snapshot.outputs_current && item.available === true && item.qualification?.scenario_ready !== false && sameProvenance(item, snapshot);
}
function amount(value: unknown, unit?: string) {
  return textValue(value) + (value != null && unit ? ' ' + (unit === 'EUR' ? '€' : unit) : '');
}

export default function SheetOutputs({ app, sheet, catalog, version }: { app: ConnectedProps; sheet: CatalogSheet; catalog: Catalog; version: string }) {
  const router = useRouter();
  const remote = useCaseData<SheetOutputSnapshot>(app.caseId, '/cockpit/sheets/' + encodeURIComponent(sheet.id) + '/outputs', version);
  const [chosenYear, setChosenYear] = useState('');
  const snapshot = remote.data;
  const arraysValid = !!snapshot && [snapshot.series, snapshot.metrics, snapshot.annual_metrics, snapshot.diagnostics].every(Array.isArray);
  const allItems = snapshot && arraysValid ? [...snapshot.series, ...snapshot.metrics, ...snapshot.annual_metrics] : [];
  const coherent = !!snapshot && arraysValid && snapshot.schema === 'tca-cockpit-outputs/1' && snapshot.case_id === app.caseId && snapshot.sheet_id === sheet.id
    && snapshot.revision === app.active?.revision && snapshot.profile_sha256 === catalog.profile_sha256
    && typeof app.active?.sha256 === 'string' && snapshot.sha256 === app.active.sha256
    && allItems.every(item => sameProvenance(item, snapshot))
    && snapshot.series.every(item => item.case_id === snapshot.case_id && item.revision === snapshot.revision);
  function sourceLink(source: CellSource | undefined, label: string) {
    if (!source) return null;
    const target = catalog.sheets.find(item => item.name === source.sheet);
    return target ? <button type="button" className="mt-1 block text-left text-xs text-[var(--brand)] underline underline-offset-4" aria-label={'Cellule de calcul · ' + label} onClick={() => router.push('/expert/feuilles/' + encodeURIComponent(target.id) + '?vue=grille&cell=' + encodeURIComponent(source.cell))}>{source.sheet} · {source.cell}</button>
      : <small className="mt-1 block text-slate-500">{source.sheet} · {source.cell}</small>;
  }
  if (!snapshot || !coherent) return <Surface>
    <h2 className="text-xl font-semibold">Résultats calculés de la feuille</h2>
    {remote.loading ? <p role="status" className="mt-3 text-slate-500">Lecture des résultats de cette révision…</p> : <>
      <p role="alert" className="mt-3 text-amber-900">{remote.error || (snapshot ? 'Les résultats lus ne correspondent pas à la révision courante de ce dossier. Actualisez la lecture avant de les consulter.' : 'Les résultats structurés ne peuvent pas être lus pour le moment. La grille du classeur reste accessible.')}</p>
      <Button variant="outline" className="mt-4 min-h-11 rounded-full" onClick={remote.retry}>Actualiser les résultats</Button>
    </>}
  </Surface>;

  const periods = [...new Set(snapshot.series.flatMap(item => item.categories))].sort();
  const years = [...new Set(periods.map(period => period.slice(0, 4)))];
  const year = years.includes(chosenYear) ? chosenYear : years[0];
  const shownPeriods = periods.filter(period => period.startsWith(year || ''));
  const reasons = [...new Set(allItems.flatMap(item => [...(item.qualification?.blockers || []), ...(item.qualification?.hypotheses || [])].map(reason => reason.message).filter((message): message is string => !!message)))];
  function metricValue(item: OutputMetric) {
    if (!available(item, snapshot!)) return 'Indisponible';
    if (item.id === 'cash_break_date' && item.value === null && item.status === 'CALCULE') return 'Aucune rupture sur la période';
    return amount(item.value, item.unit);
  }
  function metricSources(item: OutputMetric) {
    if (item.sheet && item.cell) return sourceLink({ sheet: item.sheet, cell: item.cell }, item.label);
    if (item.sources?.length === 1) return sourceLink(item.sources[0], item.label);
    return item.sources?.length ? <details className="mt-2 text-xs font-normal text-slate-500"><summary className="cursor-pointer">Cellules utilisées ({item.sources.length})</summary><div className="mt-2 max-h-48 overflow-y-auto">{item.sources.map((source, index) => <div key={source.sheet + source.cell}>{sourceLink(source, item.label + ' · ' + (index + 1))}</div>)}</div></details> : null;
  }
  function metricTable(items: OutputMetric[], label: string) {
    return <div className="overflow-x-auto"><table aria-label={label} className="mt-5 w-full min-w-[550px] text-left text-sm"><thead><tr className="border-b border-slate-200"><th className="p-3">Indicateur</th><th className="p-3">Période</th><th className="p-3">Valeur</th><th className="p-3">État</th></tr></thead><tbody>{items.map(item => <tr key={item.id} className="border-b border-slate-100"><th scope="row" className="p-3 font-medium">{item.label}{metricSources(item)}</th><td className="p-3">{item.period || 'Horizon du dossier'}</td><td className="p-3">{metricValue(item)}</td><td className="p-3 text-slate-500">{statusLabel(item.status)}</td></tr>)}</tbody></table></div>;
  }
  return <div className="space-y-5" aria-label="Résultats calculés de la feuille">
    <Surface>
      <div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-semibold">Résultats calculés de la feuille</h2><StateBadge tone={snapshot.outputs_current ? 'neutral' : 'warning'}>Révision {snapshot.revision} · {statusLabel(snapshot.calculation_status)}</StateBadge></div>
      <p className="mt-3 text-slate-500">Ces résultats appartiennent au classeur de référence. Le brouillon les fera évoluer après simulation ou application et recalcul. Une valeur indisponible reste distincte d’un zéro.</p>
      {!snapshot.outputs_current && <p role="status" className="mt-3 rounded-2xl bg-amber-50 p-4 text-amber-900">Les calculs de cette révision doivent être actualisés. Aucun montant de l’ancien calcul n’est présenté comme courant.</p>}
      {snapshot.diagnostics.length > 0 && <ul className="mt-4 list-disc space-y-2 pl-5 text-slate-600">{snapshot.diagnostics.map((message, index) => <li key={index}>{message}</li>)}</ul>}
      {reasons.length > 0 && <details className="mt-4 rounded-2xl bg-amber-50 p-4"><summary className="cursor-pointer font-medium">Qualifications et hypothèses à examiner ({reasons.length})</summary><ul className="mt-3 list-disc space-y-2 pl-5 text-slate-700">{reasons.map(message => <li key={message}>{message}</li>)}</ul></details>}
      {!allItems.length && <p className="mt-4 text-slate-500">Le moteur ne publie pas encore de résultats structurés pour cette feuille. Consultez ses cellules et formules dans la grille ; cette limitation ne signifie pas que le classeur est vide.</p>}
    </Surface>
    {snapshot.series.length > 0 && <Surface>
      <div className="flex flex-wrap items-end justify-between gap-4"><h3 className="text-lg font-semibold">Séries mensuelles</h3>{years.length > 0 && <label className="text-sm font-medium">Année affichée<select aria-label="Année des séries mensuelles" value={year} onChange={event => setChosenYear(event.target.value)} className="ml-3 min-h-11 rounded-xl border border-slate-200 bg-white px-3">{years.map(item => <option key={item}>{item}</option>)}</select></label>}</div>
      <div className="mt-5 overflow-x-auto"><table aria-label="Résultats mensuels de la feuille" className="w-full min-w-[560px] text-left text-sm"><thead><tr className="border-b border-slate-200"><th className="p-3">Mois</th>{snapshot.series.map(item => <th key={item.id} className="p-3">{item.label}<small className="mt-1 block font-normal text-slate-500">{item.unit} · {statusLabel(item.status)}</small></th>)}</tr></thead><tbody>{shownPeriods.map(period => <tr key={period} className="border-b border-slate-100"><th scope="row" className="p-3 font-medium">{period}</th>{snapshot.series.map(item => {
        const index = item.categories.indexOf(period);
        const value = index < 0 ? 'Hors période' : !available(item, snapshot) ? 'Indisponible' : amount(item.values[index], item.unit);
        return <td key={item.id} className="p-3">{value}{index >= 0 && sourceLink(item.sources[index], item.label + ' · ' + period)}</td>;
      })}</tr>)}</tbody></table></div>
    </Surface>}
    {snapshot.annual_metrics.length > 0 && <Surface><h3 className="text-lg font-semibold">Résultats annuels</h3>{metricTable(snapshot.annual_metrics, 'Résultats annuels de la feuille')}</Surface>}
    {snapshot.metrics.length > 0 && <Surface><h3 className="text-lg font-semibold">Indicateurs du dossier</h3>{metricTable(snapshot.metrics, 'Indicateurs de la feuille')}</Surface>}
  </div>;
}
