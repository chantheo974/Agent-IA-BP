import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { useRouter, useSearchParams } from '../cockpit/router';
import { Button } from '@/components/ui/button';
import { PageHeading, StateBadge, Surface } from '@/components/cockpit/page-elements';
import { ArrowLeft, FileSpreadsheet, MessageCircleQuestion, Network } from '@/components/ui/site-icon';
import { errorText, intentApi, parseValue, statusLabel, type NumericLocale } from '../api';
import type { ConnectedProps, Catalog, CatalogSheet, SheetEntry, SheetView } from './types';
import { choiceValue, textValue, useCaseData } from './data';
import SheetOutputs from './SheetOutputs';

const control = 'min-h-11 w-full rounded-2xl border border-slate-200 bg-white px-3 py-2 text-base text-slate-800 outline-none focus:ring-2 focus:ring-[var(--brand)]';
const inputText = (value: unknown) => typeof value === 'number' ? value.toLocaleString('fr-FR', { useGrouping: false, maximumSignificantDigits: 15 }) : value == null ? '' : String(value);
export const sheetHref = (id: string, view = 'metier') => '/expert/feuilles/' + encodeURIComponent(id) + '?vue=' + view;

export function ReadError({ message, retry }: { message: string; retry: () => void }) {
  return message ? <div role="alert" className="my-4 rounded-2xl bg-red-50 p-4 text-red-900"><p>{message}</p><Button variant="outline" className="mt-2 min-h-11 rounded-full" onClick={retry}>Réessayer la lecture</Button></div> : null;
}

function useUnsavedEntryGuard(dirty: boolean) {
  useEffect(() => {
    if (!dirty) return;
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ''; };
    const guard = (event: Event) => {
      if (!event.defaultPrevented && !window.confirm('Des saisies ne sont pas encore proposées au brouillon. Quitter cette feuille ?')) event.preventDefault();
    };
    window.addEventListener('beforeunload', warn);
    window.addEventListener('cockpit:before-navigation', guard);
    return () => { window.removeEventListener('beforeunload', warn); window.removeEventListener('cockpit:before-navigation', guard); };
  }, [dirty]);
}

function normalized(text: string, kind: string | undefined, locale: NumericLocale) {
  if (kind === 'text' || kind === 'string') return text || null;
  const value = parseValue(text, locale);
  if (text.trim() && ['number', 'integer', 'percent'].includes(kind || '') && typeof value !== 'number') {
    throw new Error(`« ${text} » n’est pas un nombre reconnu au format ${locale === 'fr' ? 'français' : 'anglais'}. Vérifiez la conversion avant de proposer.`);
  }
  return value;
}

export function SheetPanel({ app, sheet, catalog, discuss, version }: { app: ConnectedProps; sheet: CatalogSheet; catalog: Catalog; discuss: (sheet: string) => void; version: string }) {
  const router = useRouter(), params = useSearchParams();
  const view = params.get('vue') || 'metier';
  const [offset, setOffset] = useState(0);
  const remote = useCaseData<SheetView>(app.caseId, '/cockpit/sheets/' + encodeURIComponent(sheet.id) + '?offset=' + offset + '&limit=100', version);
  const [edits, setEdits] = useState<Record<string, { entry: SheetEntry; text: string; revision: number }>>({});
  const [source, setSource] = useState(''), [status, setStatus] = useState('HYPOTHESE');
  const [locale, setLocale] = useState<NumericLocale>('fr'), [busy, setBusy] = useState(false), [error, setError] = useState('');
  const [mode, setMode] = useState<'guided' | 'auto'>('guided');
  const dirty = Object.keys(edits).length > 0;
  useUnsavedEntryGuard(dirty);
  useEffect(() => {
    app.onSheet(sheet.name, params.get('cell') || undefined);
    // A stable route is resolved through this dossier's server-side profile.
  }, [sheet.name, params.get('cell'), app.onSheet]);
  async function propose(event: FormEvent) {
    event.preventDefault(); if (!remote.data || !source || app.blocked || busy) return;
    setBusy(true); setError('');
    try {
      if (Object.values(edits).some(edit => edit.revision !== remote.data!.revision)) throw new Error('Le dossier a changé depuis vos saisies. Annulez ces saisies puis comparez les nouvelles valeurs avant de préparer un autre lot.');
      const answers = Object.values(edits).map(({ entry, text }) => ({ sheet_id: sheet.id, binding_id: entry.binding_id, value: normalized(text, entry.value_type, locale), evidence_id: source, status, reason: 'Saisie dans le parcours métier du cockpit' }));
      await intentApi(app.caseId, '/cockpit/answers', 'POST', { expected_revision: remote.data.revision, answers });
      setEdits({}); await app.onRefresh(); remote.retry(); app.onDraft();
    } catch (e) { setError(errorText(e)); } finally { setBusy(false); }
  }
  const entries = remote.data?.entries || [];
  const controls = <div className="mt-6 flex flex-wrap gap-2">{[['metier', 'Vue métier'], ['grille', 'Grille Excel'], ['liens', 'Dépendances']].map(([id, label]) => <Button key={id} variant={view === id ? 'default' : 'outline'} className="min-h-11 rounded-full px-5" aria-pressed={view === id} onClick={() => router.replace(sheetHref(sheet.id, id), { scroll: false })}>{label}</Button>)}</div>;
  return <div className="space-y-6">
    <Button variant="ghost" className="min-h-11 rounded-full" onClick={() => router.push('/expert')}><ArrowLeft />Toutes les feuilles</Button>
    <PageHeading eyebrow="Feuille du dossier" title={sheet.label || sheet.name} description={sheet.purpose || sheet.role || 'Consultez les données de cette feuille et préparez vos modifications.'} actions={<Button className="min-h-11 rounded-full px-5" onClick={() => discuss(sheet.name)}><MessageCircleQuestion />Discuter de cette feuille</Button>} />
    <div className="flex flex-wrap gap-2"><StateBadge tone="neutral">{sheet.name}</StateBadge><StateBadge>Révision {remote.data?.revision ?? catalog.revision}</StateBadge><StateBadge tone="warning">{statusLabel(remote.data?.calculation_status || catalog.calculation_status)}</StateBadge>{remote.data?.draft.current && <StateBadge>Propositions du brouillon affichées</StateBadge>}</div>
    {controls}
    <ReadError message={remote.error} retry={remote.retry}/>
    {view === 'grille' && <Surface className="overflow-hidden p-2 sm:p-3"><p className="px-3 py-2 text-sm text-slate-500">Les entrées métier reconnues rejoignent le brouillon partagé. Les formules et la structure sont conservées. Les résultats financiers nécessitent le recalcul et les qualifications du dossier.</p><div className="legacy-ui connected-grid" style={{ minHeight: 620 }}>{app.grid(() => discuss(''))}</div></Surface>}
    {view === 'liens' && <Surface><h2 className="flex items-center gap-2 text-xl font-semibold"><Network />Feuilles liées par le contrat métier</h2><p className="mt-2 text-slate-500">Ces liens proviennent du profil versionné du dossier. Les conséquences chiffrées apparaissent après simulation ou recalcul.</p><div className="mt-5 grid gap-3 sm:grid-cols-2">{sheet.dependencies.map(dependency => <Button key={dependency.id} variant="outline" className="min-h-14 justify-start rounded-2xl px-4" onClick={() => router.push(sheetHref(dependency.id))}><FileSpreadsheet />{dependency.label || dependency.name}</Button>)}</div>{!sheet.dependencies.length && <p className="mt-5 text-slate-500">Aucune dépendance déclarée pour cette feuille.</p>}<p className="mt-5 text-sm text-slate-500">Profil {catalog.profile_version} · {sheet.field_count} champs métier.</p></Surface>}
    {view === 'metier' && <>
      {remote.data && (remote.data.total === 0 || ['series', 'statements', 'controls', 'valuation', 'sensitivity'].includes(sheet.view_kind)) && <SheetOutputs app={app} sheet={sheet} catalog={catalog} version={version}/>}
      <div className="flex flex-wrap gap-2">{[['guided', 'Guide-moi'], ['auto', 'Fais-le pour moi']].map(([id, label]) => <Button key={id} className="min-h-11 rounded-full px-5" variant={mode === id ? 'default' : 'outline'} onClick={() => setMode(id as 'guided' | 'auto')}>{label}</Button>)}</div>
      {mode === 'auto' ? <Surface variant="tinted"><h2 className="text-xl font-semibold">Préparer une proposition avec le compagnon</h2><p className="mt-3 leading-7 text-slate-600">Décrivez la décision et ses sources. Le compagnon travaille sur cette feuille, pose les questions nécessaires et prépare un lot que vous pourrez examiner. Aucune modification n’est appliquée par ce bouton.</p><Button className="mt-5 min-h-11 rounded-full px-5" onClick={() => discuss(sheet.name)}>Ouvrir le compagnon de cette feuille</Button></Surface> : <Surface>
        <h2 className="text-xl font-semibold">Entrées et hypothèses</h2><p className="mt-2 text-slate-500">Les données actuelles et les propositions sont séparées. Sélectionnez une source pour proposer vos changements.</p>
        {remote.loading && !remote.data && <p role="status" className="mt-5">Lecture des champs du dossier…</p>}
        {error && <p role="alert" className="mt-4 rounded-2xl bg-red-50 p-4 text-red-800">{error}</p>}
        <form onSubmit={event => void propose(event)} className="mt-5 space-y-5">
          {!!entries.length && <><div className="grid gap-4 md:grid-cols-3"><label className="space-y-2 text-sm font-medium">Source des modifications<select aria-label="Source des modifications" className={control} value={source} onChange={e => setSource(e.target.value)} required><option value="">Choisir une source du dossier</option>{app.sources.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><label className="space-y-2 text-sm font-medium">État documentaire<select aria-label="État documentaire" className={control} value={status} onChange={e => setStatus(e.target.value)}><option value="HYPOTHESE">Hypothèse à confirmer</option><option value="CONFIRME">Information confirmée</option></select></label><label className="space-y-2 text-sm font-medium">Format des nombres<select aria-label="Format des nombres" className={control} value={locale} onChange={e => setLocale(e.target.value as NumericLocale)}><option value="fr">Français : 1 234,56</option><option value="en">Anglais : 1,234.56</option></select></label></div>
          <div className="overflow-x-auto"><table className="w-full min-w-[600px] border-separate border-spacing-y-2 text-left text-sm"><thead><tr><th className="p-2">Information</th><th className="p-2">Dossier actuel</th><th className="p-2">Proposition</th></tr></thead><tbody>{entries.map(entry => <tr key={entry.binding_id} className="bg-slate-50/80"><th scope="row" className="rounded-l-2xl p-3 font-medium"><span>{entry.label}</span><span className="mt-1 block text-xs font-normal text-slate-500">{entry.cell} · {entry.unit || entry.value_type || 'Valeur'} · {statusLabel(entry.status)}{entry.calculated ? ' · formule conservée' : ''}</span>{entry.evidence_id && <span className="block text-xs font-normal text-slate-500">Source : {app.sources.find(item => item.id === entry.evidence_id)?.title || 'Référence documentaire'}</span>}</th><td className="p-3">{textValue(entry.current_value)}{entry.formula && <details className="mt-1 text-xs text-slate-500"><summary>Formule</summary><code>{entry.formula}</code></details>}</td><td className="rounded-r-2xl p-3">{entry.editable && !entry.calculated ? <><input className={control} aria-label={entry.label + ' · ' + entry.cell} value={edits[entry.binding_id]?.text ?? inputText(entry.value)} list={'choices-' + entry.binding_id} disabled={busy || app.blocked} onChange={e => setEdits(current => ({ ...current, [entry.binding_id]: { entry, text: e.target.value, revision: current[entry.binding_id]?.revision ?? remote.data!.revision } }))}/><datalist id={'choices-' + entry.binding_id}>{(entry.choices || []).map((item, i) => <option key={i} value={choiceValue(item)}/>)}</datalist>{edits[entry.binding_id] && <span className="mt-1 block text-xs text-[var(--brand)]">Conversion : {textValue(parseValue(edits[entry.binding_id].text, locale))}</span>}{entry.proposed && !edits[entry.binding_id] && <span className="mt-1 block text-xs text-[var(--brand)]">Déjà au brouillon</span>}</> : <span className="text-slate-500">{textValue(entry.value)}<small className="mt-1 block">{entry.reason || 'Lecture seule ; cette cellule conserve la formule et le rôle définis par le modèle.'}</small></span>}</td></tr>)}</tbody></table></div>
          <div className="flex flex-wrap items-center gap-3"><Button type="button" variant="outline" className="min-h-11 rounded-full px-5" onClick={app.onSource}>Ajouter une source</Button><Button className="min-h-11 rounded-full px-5" type="submit" disabled={!dirty || !source || busy || app.blocked}>Proposer {Object.keys(edits).length || ''} modification(s) au brouillon</Button>{dirty && <Button type="button" variant="ghost" className="min-h-11 rounded-full" onClick={() => setEdits({})}>Annuler ces saisies</Button>}</div>
          <div className="flex items-center justify-between gap-3 text-sm text-slate-500"><Button type="button" variant="outline" disabled={offset === 0 || remote.loading} onClick={() => setOffset(n => Math.max(0, n - 100))}>Précédent</Button><span>{Math.min(offset + 1, remote.data?.total || 0)}–{Math.min(offset + 100, remote.data?.total || 0)} sur {remote.data?.total || 0} entrées</span><Button type="button" variant="outline" disabled={offset + 100 >= (remote.data?.total || 0) || remote.loading} onClick={() => setOffset(n => n + 100)}>Suivant</Button></div></>}
          {!remote.loading && !entries.length && !remote.error && <><p className="text-slate-500">Cette feuille se consulte à travers ses résultats calculés et sa grille. Elle ne comporte pas de formulaire de saisie catalogué ; les cellules et formules restent accessibles.</p><Button type="button" className="min-h-11 rounded-full px-5" onClick={() => router.replace(sheetHref(sheet.id, 'grille'))}>Consulter la grille de cette feuille</Button></>}
        </form>
      </Surface>}
      {sheet.register?.can_add && <RecordForm key={sheet.id} app={app} sheet={sheet} revision={catalog.revision}/>}
    </>}
    {!['metier', 'grille', 'liens'].includes(view) && <Surface><p>Cette vue n’existe pas.</p><Button onClick={() => router.replace(sheetHref(sheet.id))}>Revenir à la vue métier</Button></Surface>}
  </div>;
}

function RecordForm({ app, sheet, revision }: { app: ConnectedProps; sheet: CatalogSheet; revision: number }) {
  const [values, setValues] = useState<Record<string, string>>({}), [source, setSource] = useState('');
  const [locale, setLocale] = useState<NumericLocale>('fr'), [busy, setBusy] = useState(false), [error, setError] = useState('');
  const [questions, setQuestions] = useState<{ question?: string; message?: string }[]>([]);
  const fields = sheet.fields.filter(field => field.can_propose);
  const baseRevision = useRef(revision);
  useUnsavedEntryGuard(Object.keys(values).length > 0);
  useEffect(() => { if (!Object.keys(values).length) baseRevision.current = revision; }, [revision, values]);
  async function submit(event: FormEvent) {
    event.preventDefault(); if (!source || app.blocked || busy) return; setBusy(true); setError('');
    try {
      if (baseRevision.current !== revision) throw new Error('Le dossier a changé depuis cette saisie. Conservez vos informations puis recommencez le formulaire sur la nouvelle révision.');
      const supplied = Object.fromEntries(fields.filter(field => Object.hasOwn(values, field.field_id)).map(field => [field.field_id, normalized(values[field.field_id], field.value_type, locale)]));
      const result = await intentApi<{ status?: string; questions?: { question?: string; message?: string }[]; message?: string }>(app.caseId, '/cockpit/sheets/' + encodeURIComponent(sheet.id) + '/records', 'POST', { expected_revision: revision, evidence_id: source, values: supplied });
      if (['NEEDS_INPUT', 'REFUSED'].includes(result.status || '')) { setQuestions(result.questions || []); if (result.message) setError(result.message); return; }
      setValues({}); setQuestions([]); await app.onRefresh(); app.onDraft();
    } catch (e) { setError(errorText(e)); } finally { setBusy(false); }
  }
  return <Surface variant="glass"><h2 className="text-xl font-semibold">Ajouter une opération dans {sheet.label}</h2><p className="mt-2 text-slate-500">Le registre vérifie les informations et conserve ses formules. L’opération sera proposée dans le même brouillon.</p>{error && <p role="alert" className="mt-3 text-red-800">{error}</p>}{questions.length > 0 && <div role="status" className="mt-4 rounded-2xl bg-amber-50 p-4"><h3 className="font-semibold">Informations à préciser</h3><ul className="mt-2 list-disc pl-5">{questions.map((question, i) => <li key={i}>{question.question || question.message}</li>)}</ul></div>}<form onSubmit={event => void submit(event)} className="mt-5 space-y-5"><div className="grid gap-4 md:grid-cols-2">{fields.map(field => <label className="space-y-2 text-sm font-medium" key={field.field_id}>{field.label || field.field_id}{field.unit && <span className="ml-1 text-slate-500">({field.unit})</span>}<input className={control} aria-label={'Nouvelle opération · ' + field.label} value={values[field.field_id] || ''} list={'record-' + field.field_id} onChange={e => setValues(current => ({ ...current, [field.field_id]: e.target.value }))}/><datalist id={'record-' + field.field_id}>{(field.choices || []).map((choice, i) => <option key={i} value={choiceValue(choice)}/>)}</datalist></label>)}</div><div className="grid gap-4 md:grid-cols-2"><label className="space-y-2 text-sm font-medium">Source de l’opération<select aria-label="Source de l’opération" className={control} value={source} required onChange={e => setSource(e.target.value)}><option value="">Choisir une source</option>{app.sources.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><label className="space-y-2 text-sm font-medium">Format des nombres<select aria-label="Format des nombres" className={control} value={locale} onChange={e => setLocale(e.target.value as NumericLocale)}><option value="fr">Français : 1 234,56</option><option value="en">Anglais : 1,234.56</option></select></label></div><div className="flex flex-wrap gap-2"><Button type="button" variant="outline" className="min-h-11 rounded-full px-5" onClick={app.onSource}>Ajouter une source</Button><Button type="submit" className="min-h-11 rounded-full px-5" disabled={!source || busy || app.blocked}>Préparer cette opération</Button>{Object.keys(values).length > 0 && <Button type="button" variant="ghost" className="min-h-11 rounded-full" onClick={() => { setValues({}); setQuestions([]); setError(''); }}>Annuler cette saisie</Button>}</div></form></Surface>;
}

export function Legacy({ children, className = '' }: { children: ReactNode; className?: string }) { return <div className={'legacy-ui ' + className}>{children}</div>; }
