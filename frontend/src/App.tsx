import { lazy, Suspense, useCallback, useEffect, useRef, useState, type CSSProperties, type KeyboardEvent, type PointerEvent } from "react";
import { ApiError, api, casePath, downloadFile, errorText, intentApi, isRunning, statusLabel, type IntentReviewRequest } from "./api";
import { ChartsDialog, DraftDialog, IntentReviewDialog, JobsDialog, NewCaseDialog, SettingsDialog, SourceDialog, StructureDialog, VersionsDialog } from "./Dialogs";
import type { Agent, Case, Draft, Job, Message, Operation, Scope, Sheet, Source, Version } from "./types";
import { Button, Empty, Icon } from "./ui";
import WorkbookGrid from "./WorkbookGrid";
import { workshopPages, type WorkshopPage } from "./workshopTypes";
const Workshop = lazy(() => import("./Workshop"));
const ConnectedCockpit = lazy(() => import("./connected/ConnectedCockpit"));

type ChartData = Parameters<typeof ChartsDialog>[0]["data"];
type Dialog = "new" | "source" | "settings" | "draft" | "versions" | "charts" | "jobs" | null;
const noDraft: Draft = { status: "EMPTY", operations: [], changes: [], conflicts: [] };
const dateText = (value?: string) => value ? new Date(value).toLocaleDateString("fr-FR", { day: "numeric", month: "short" }) : "";

function ResizeHandle({ side, value, change }: { side: "left" | "right"; value: number; change: (width: number) => void }) {
  function start(event: PointerEvent<HTMLDivElement>) {
    event.preventDefault(); event.currentTarget.setPointerCapture(event.pointerId);
    const first = event.clientX, width = value, target = event.currentTarget;
    const move = (next: globalThis.PointerEvent) => change(Math.max(side === "left" ? 210 : 300, Math.min(side === "left" ? 440 : 620, width + (next.clientX - first) * (side === "left" ? 1 : -1))));
    const stop = () => { target.removeEventListener("pointermove", move); target.removeEventListener("pointerup", stop); target.removeEventListener("pointercancel", stop); };
    target.addEventListener("pointermove", move); target.addEventListener("pointerup", stop); target.addEventListener("pointercancel", stop);
  }
  return <div className="resize-handle" role="separator" tabIndex={0} aria-orientation="vertical" aria-label={side === "left" ? "Largeur du panneau de navigation" : "Largeur du panneau de conversation"} aria-valuenow={value} onPointerDown={start} onKeyDown={event => { if (event.key === "ArrowLeft" || event.key === "ArrowRight") { event.preventDefault(); change(Math.max(side === "left" ? 210 : 300, Math.min(side === "left" ? 440 : 620, value + (event.key === "ArrowRight" ? 20 : -20) * (side === "left" ? 1 : -1)))); } }}/>
}

export default function App({ cockpit = false }: { cockpit?: boolean } = {}) {
  const [cases, setCases] = useState<Case[]>([]), [caseId, setCaseId] = useState(() => localStorage.getItem("tca.case") || "");
  const selectedRef = useRef(caseId); selectedRef.current = caseId;
  const [detail, setDetail] = useState<Case | null>(null), [sheets, setSheets] = useState<Sheet[]>([]), [sheetName, setSheetName] = useState("");
  const [sources, setSources] = useState<Source[]>([]), [agents, setAgents] = useState<Agent[]>([]), [draft, setDraft] = useState<Draft>(noDraft);
  const [messages, setMessages] = useState<Message[]>([]), [jobs, setJobs] = useState<Job[]>([]), [versions, setVersions] = useState<Version[]>([]), [charts, setCharts] = useState<ChartData>({ charts: [] });
  const [dialog, setDialog] = useState<Dialog>(null), [structure, setStructure] = useState<{ kind: string; index: number } | null>(null);
  const [error, setError] = useState(""), [notice, setNotice] = useState(""), [busyCounts, setBusyCounts] = useState<Record<string, number>>({}), [initializing, setInitializing] = useState(true);
  const busy = (busyCounts[caseId] || 0) > 0;
  const [scope, setScope] = useState<Scope>({ sheet: "", range: "A1" }), [wholeSheet, setWholeSheet] = useState(false), [allowStructure, setAllowStructure] = useState(false);
  const [leftTab, setLeftTab] = useState("sheets"), [rightTab, setRightTab] = useState("chat"), [sheetFilter, setSheetFilter] = useState(""), [agentFilter, setAgentFilter] = useState("");
  const [chatText, setChatText] = useState(""), [evidence, setEvidence] = useState(""), [gridRefresh, setGridRefresh] = useState(0);
  const [pendingChat, setPendingChat] = useState(false);
  const [connectedRefresh, setConnectedRefresh] = useState(0);
  const [intentReview, setIntentReview] = useState<IntentReviewRequest | null>(null);
  useEffect(() => { const receive = (event: Event) => setIntentReview((event as CustomEvent<IntentReviewRequest>).detail); window.addEventListener("tca-intent-review", receive); return () => window.removeEventListener("tca-intent-review", receive); }, []);
  const [connection, setConnection] = useState("connecting"), [liveStatus, setLiveStatus] = useState("");
  const [leftWidth, setLeftWidth] = useState(() => Number(localStorage.getItem("tca.leftWidth")) || 260), [rightWidth, setRightWidth] = useState(() => Number(localStorage.getItem("tca.rightWidth")) || 360);
  const [leftOpen, setLeftOpen] = useState(true), [rightOpen, setRightOpen] = useState(true);
  const [gridTarget, setGridTarget] = useState<{ sheet: string; cell: string } | null>(null);
  const [page, setPage] = useState<WorkshopPage>(() => { const saved = localStorage.getItem("tca.page." + caseId); return workshopPages.some(p => p.id === saved) ? saved as WorkshopPage : "forecast"; }), [guided, setGuided] = useState(false), [extraSheets, setExtraSheets] = useState<string[]>([]);
  const messageEnd = useRef<HTMLDivElement>(null), chatInput = useRef<HTMLTextAreaElement>(null);
  const refreshPending = useRef(false);
  const active = detail?.id === caseId ? detail : null;
  const sheet = sheets.find(item => item.name === sheetName);
  const running = jobs.filter(job => isRunning(job.status));
  const chatRunning = running.some(job => job.kind.toLowerCase().includes("chat"));
  const mutating = busy || running.some(job => !job.kind.toLowerCase().includes("chat")) || draft.status === "PREPARING";
  const hasDraft = !!draft.operations?.length || !!draft.conflicts?.length;
  const ready = draft.status === "READY" && !!draft.approval_token && !draft.conflicts?.length;
  const chatScope: Scope = extraSheets.length ? { ...(wholeSheet ? {} : scope), sheet: sheetName, sheets: [...new Set([sheetName, ...extraSheets])], allow_structure: allowStructure } : wholeSheet ? { sheet: sheetName, ...(allowStructure ? { allow_structure: true } : {}) } : { ...scope, sheet: sheetName };

  const refreshCases = useCallback(async () => {
    try { const result = await api<{ cases: Case[] }>("/cases"); setCases(result.cases); setCaseId(current => result.cases.some(item => item.id === current) ? current : result.cases[0]?.id || ""); }
    catch (e) { setError(errorText(e)); } finally { setInitializing(false); }
  }, []);
  const refreshCase = useCallback(async () => {
    if (!caseId) return;
    const paths = ["", "/sheets", "/sources", "/draft", "/chat", "/agents", "/jobs"];
    const results = await Promise.allSettled(paths.map(path => api<unknown>(casePath(caseId) + path)));
    if (selectedRef.current !== caseId) return;
    results.forEach((result, index) => {
      if (result.status === "rejected") { setError(errorText(result.reason)); return; }
      const value = result.value as Record<string, unknown>;
      if (index === 0) setDetail((value.case || value) as Case);
      if (index === 1) { const next = (value.sheets || []) as Sheet[]; setSheets(next); setSheetName(current => next.some(item => item.name === current) ? current : next.find(item => item.name === "Control")?.name || next[0]?.name || ""); }
      if (index === 2) setSources((value.sources || []) as Source[]);
      if (index === 3) setDraft((value.draft || value) as Draft);
      if (index === 4) setMessages((value.messages || []) as Message[]);
      if (index === 5) setAgents((value.agents || []) as Agent[]);
      if (index === 6) setJobs((value.jobs || []) as Job[]);
    });
    if (cockpit) setConnectedRefresh(value => value + 1);
  }, [caseId, cockpit]);
  useEffect(() => { void refreshCases(); }, [refreshCases]);
  useEffect(() => {
    localStorage.setItem("tca.case", caseId); setDetail(null); setSheets([]); setSources([]); setAgents([]); setDraft(noDraft); setJobs([]); setMessages([]); setEvidence(""); setChatText(""); setLiveStatus(""); setWholeSheet(false); setAllowStructure(false); setDialog(null);
    void refreshCase();
    setExtraSheets([]);
    setChatText(localStorage.getItem("tca.chat.draft." + caseId) || "");
    setPendingChat(!!localStorage.getItem("tca.chat.pending." + caseId));
  }, [caseId, refreshCase]);
  useEffect(() => { setGridRefresh(n => n + 1); }, [active?.revision, active?.id]);
  useEffect(() => { localStorage.setItem("tca.leftWidth", String(leftWidth)); }, [leftWidth]);
  useEffect(() => { localStorage.setItem("tca.rightWidth", String(rightWidth)); }, [rightWidth]);
  useEffect(() => { if (caseId) localStorage.setItem("tca.page." + caseId, page); }, [caseId, page]);
  useEffect(() => { messageEnd.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [messages.length, liveStatus]);
  const [streamAttempt, setStreamAttempt] = useState(0);
  useEffect(() => {
    if (!caseId) return;
    setConnection("connecting");
    const events = new EventSource("/api" + casePath(caseId) + "/events");
    let timer: ReturnType<typeof setTimeout> | undefined, rebuild: ReturnType<typeof setTimeout> | undefined;
    const reload = () => { if (timer) clearTimeout(timer); timer = setTimeout(() => void refreshCase(), 250); };
    // Une reconnexion réussie relit le dossier : les événements manqués pendant
    // la coupure ne reviendront pas d'eux-mêmes.
    events.onopen = () => { setConnection("connected"); reload(); };
    events.onerror = () => {
      setConnection("retrying");
      // Le navigateur ne retente jamais un flux définitivement fermé, par exemple
      // après une réponse d'erreur. Sans reconstruction, l'atelier resterait sur
      // un état figé tout en affichant « Reconnexion ».
      if (events.readyState === EventSource.CLOSED && !rebuild) rebuild = setTimeout(() => setStreamAttempt(value => value + 1), 3000);
    };
    events.addEventListener("refresh", reload);
    events.addEventListener("resync", () => { setGridRefresh(n => n + 1); reload(); });
    events.addEventListener("job", reload);
    events.addEventListener("chat", event => {
      try { const data = JSON.parse((event as MessageEvent).data); const item = data.payload || data; if (typeof item.message === "string" && item.type === "status") setLiveStatus(item.message); } catch { /* Un événement incomplet sera remplacé par la lecture du serveur. */ }
      reload();
    });
    return () => { events.close(); if (timer) clearTimeout(timer); if (rebuild) clearTimeout(rebuild); };
  }, [caseId, refreshCase, streamAttempt]);
  useEffect(() => {
    if (!caseId || !running.length) return;
    const timer = setInterval(async () => {
      if (refreshPending.current) return;
      refreshPending.current = true;
      try { const next = await api<{ jobs: Job[] }>(casePath(caseId) + "/jobs"); if (selectedRef.current !== caseId) return; setJobs(next.jobs); if (next.jobs.some(job => !isRunning(job.status) && running.some(old => old.id === job.id))) { setLiveStatus(""); await refreshCase(); } }
      catch (e) { if (selectedRef.current === caseId) setError(errorText(e)); } finally { refreshPending.current = false; }
    }, 2000);
    return () => clearInterval(timer);
  }, [caseId, running.map(job => job.id).join(","), refreshCase]);
  const updateScope = useCallback((value: Scope) => { setScope(value); }, []);
  // Un identifiant de demande désigne une intention, pas une tentative : le
  // serveur refuse un doublon et renvoie le travail déjà créé. Il n'est renouvelé
  // qu'après une réponse du serveur ; une coupure de transport le conserve, sinon
  // un second envoi créerait un deuxième recalcul ou un deuxième appel au fournisseur.
  async function action(path: string, body?: unknown, method = "POST", success?: string, key?: string) {
    if (!caseId) return;
    const selected = caseId; setBusyCounts(counts => ({ ...counts, [selected]: (counts[selected] || 0) + 1 })); setError(""); setNotice("");
    try {
      const result = key ? await intentApi<{ job?: Job }>(selected, path, method, (body || {}) as Record<string, unknown>) : await api<{ job?: Job }>(casePath(selected) + path, method, body);
      if (selectedRef.current === selected) { if (result?.job) setJobs(previous => [result.job!, ...previous.filter(job => job.id !== result.job!.id)]); if (success) setNotice(success); await refreshCase(); }
      return result;
    } catch (e) {
      if (selectedRef.current === selected) setError(errorText(e));
      throw e;
    } finally { setBusyCounts(counts => ({ ...counts, [selected]: Math.max(0, (counts[selected] || 0) - 1) })); }
  }
  async function edit(operations: Operation[], currentScope: Scope, expectedRevision?: number) {
    if (cockpit && operations.some(operation => operation.type !== "set_value")) {
      const message = "Le cockpit modifie uniquement les entrées métier reconnues. Les formules et la structure nécessitent l’atelier de maintenance du modèle.";
      setError(message); throw new Error(message);
    }
    await action(cockpit ? "/cockpit/operations" : "/draft/operations", { operations: operations.map(op => evidence ? { ...op, evidence_id: evidence } : op), scope: currentScope, expected_revision: expectedRevision ?? active?.revision ?? 0 }, "POST", undefined, "draft");
  }
  async function sendChat(event?: FormEventLike) {
    event?.preventDefault(); if (!chatText.trim() || !sheetName || chatRunning || busy) return;
    const message = chatText.trim();
    const id = caseId;
    localStorage.setItem("tca.chat.draft." + id, message);
    let selection = cockpit ? { ...chatScope, allow_structure: false } : chatScope;
    try { const pending = JSON.parse(localStorage.getItem("tca.chat.pending." + id) || "null"); if (pending?.message === message && pending.selection) selection = cockpit ? { ...pending.selection, allow_structure: false } : pending.selection; } catch { /* An invalid saved composer cannot control a new request. */ }
    localStorage.setItem("tca.chat.pending." + id, JSON.stringify({ message, selection })); setPendingChat(true);
    try { await action("/chat", { message, selection, ...(cockpit ? { mode: "cockpit", expected_revision: active?.revision ?? 0 } : {}) }, "POST", undefined, "chat"); localStorage.removeItem("tca.chat.draft." + id); localStorage.removeItem("tca.chat.pending." + id); if (selectedRef.current === id) { setChatText(""); setPendingChat(false); setLiveStatus(""); } }
    catch (error) { if (error instanceof ApiError && error.status >= 400 && error.status < 500 && ![408, 429].includes(error.status) && !JSON.stringify(error.detail || {}).includes('"review_required":true')) { localStorage.removeItem("tca.chat.pending." + id); if (selectedRef.current === id) setPendingChat(false); } }
  }
  async function openVersions() { setError(""); try { const result = await api<{ versions: Version[] }>(casePath(caseId) + "/versions"); setVersions(result.versions); setDialog("versions"); } catch (e) { setError(errorText(e)); } }
  async function openCharts() { setError(""); try { const result = await api<ChartData>(casePath(caseId) + "/charts"); setCharts(result); setDialog("charts"); } catch (e) { setError(errorText(e)); } }
  async function downloadWorkbook() { const selected = caseId; setError(""); try { await downloadFile(casePath(selected) + "/download", "TCA_BP.xlsm"); } catch (e) { if (selectedRef.current === selected) setError(errorText(e)); } }
  const ignore = (promise: Promise<unknown>) => void promise.catch(() => {});
  const chooseCase = (id: string) => { selectedRef.current = id; setCaseId(id); setSheetName(""); const saved = localStorage.getItem("tca.page." + id); setPage(workshopPages.some(p => p.id === saved) ? saved as WorkshopPage : "forecast"); setGuided(false); };
  const unreadErrors = jobs.filter(job => ["FAILED", "INTERRUPTED"].includes(job.status));
  const layout = { "--left-width": leftOpen ? `${leftWidth}px` : "0px", "--right-width": rightOpen ? `${rightWidth}px` : "0px", "--left-handle": leftOpen ? "5px" : "0px", "--right-handle": rightOpen ? "5px" : "0px" } as CSSProperties;

  const selectConnectedSheet = useCallback((name: string, cell?: string) => {
    setSheetName(name); setPage("forecast"); setGuided(false); setWholeSheet(false); setExtraSheets([]);
    setScope({ sheet: name, range: cell || "A1" }); setGridTarget(cell ? { sheet: name, cell } : null);
  }, []);
  const dialogs = <>
    {dialog === "new" && <NewCaseDialog close={() => setDialog(null)} done={id => { chooseCase(id); setPage("company"); setDialog(null); void refreshCases(); }}/ >}
    {dialog === "source" && active && <SourceDialog caseId={caseId} close={() => setDialog(null)} done={() => { setDialog(null); setLeftTab("sources"); void refreshCase(); }}/ >}
    {dialog === "settings" && <SettingsDialog close={() => setDialog(null)}/>}
    {dialog === "draft" && active && <DraftDialog error={error} draft={draft} caseId={caseId} busy={mutating || !!running.length} close={() => setDialog(null)} preview={() => ignore(action("/draft/preview", {}))} apply={() => ignore(action("/draft/apply", { draft_id: draft.id, approval_token: draft.approval_token }, "POST", undefined, "apply:" + draft.id).then(() => { setDialog(null); void refreshCases(); }))} discard={() => ignore(action("/draft", undefined, "DELETE").then(() => setDialog(null)))} resolve={(index, choice) => ignore(action("/draft/resolve", { index, choice }))}/>}
    {dialog === "versions" && active && <VersionsDialog error={error} versions={versions} busy={mutating} close={() => setDialog(null)} restore={version => ignore(action("/versions/" + encodeURIComponent(version.id) + "/restore", {}, "POST", undefined, "restore:" + version.id).then(() => { setDialog(null); void refreshCases(); }))}/>}
    {dialog === "jobs" && <JobsDialog error={error} jobs={jobs} busy={mutating || !!running.length} close={() => setDialog(null)} cancel={job => ignore(action("/jobs/" + encodeURIComponent(job.id) + "/cancel", {}, "POST", "Interruption demandée. Les points terminés restent conservés.", "cancel:" + job.id))} retry={job => ignore(action("/jobs/" + encodeURIComponent(job.id) + "/retry", {}, "POST", undefined, "retry:" + job.id))}/> }
    {dialog === "charts" && <ChartsDialog data={charts} close={() => setDialog(null)}/>}
    {intentReview && <IntentReviewDialog key={intentReview.requestId} request={intentReview} close={() => setIntentReview(null)} done={() => { const reviewed = intentReview; setIntentReview(null); setError(""); setNotice("Demande clôturée après examen. Les données sont conservées ; aucune opération n’a été relancée."); if (reviewed.path === "/chat") { localStorage.removeItem("tca.chat.pending." + reviewed.caseId); if (selectedRef.current === reviewed.caseId) setPendingChat(false); } if (selectedRef.current === reviewed.caseId) void refreshCase(); }}/>}
    {structure && active && <StructureDialog kind={structure.kind} sheet={sheetName} index={structure.index} close={() => setStructure(null)} submit={op => edit([op], { sheet: op.sheet || op.name || sheetName, allow_structure: true })}/>}
  </>;
  const chatPanel = <>
      <aside className={"right-panel " + (!rightOpen ? "collapsed" : "")} aria-label="Chat et agents"><div className="assistant-heading"><span className="assistant-mark"><Icon name="spark" size={20}/></span><div><strong>L’atelier, avec vous</strong><small>Conversation & agents de feuille</small></div></div><div className="right-tabs"><button className={rightTab === "chat" ? "active" : ""} onClick={() => setRightTab("chat")}><Icon name="chat" size={15}/>Conversation</button><button className={rightTab === "agents" ? "active" : ""} onClick={() => setRightTab("agents")}><Icon name="table" size={15}/>Agents <span>{agents.length}</span></button></div>
        {rightTab === "chat" ? <><div className="conversation" aria-live="polite">{messages.length ? messages.map(message => <article className={"message " + (message.role === "user" ? "user" : "assistant")} key={message.id}><div className="message-author">{message.role === "user" ? "Vous" : message.role === "system" ? "Système" : "Assistant"}{message.status && <span>{statusLabel(message.status)}</span>}</div><div className="message-content">{message.content}</div>{!!message.agents?.length && <div className="agent-tags">{message.agents.map((agent, index) => <span key={index}>{typeof agent === "string" ? agent : agent.sheet || agent.id}</span>)}</div>}</article>) : <div className="chat-welcome"><div className="chat-orbit"><Icon name="spark" size={28}/></div><h2>Que souhaitez-vous<br/>faire évoluer ?</h2><p>Expliquez votre besoin. Le coordinateur mobilisera les agents concernés et proposera un lot à examiner.</p>{["Explique les calculs de cette feuille", "Quelles informations manquent dans ce dossier ?", "Aide-moi à construire une hypothèse de croissance"].map(prompt => <button key={prompt} disabled={!active} onClick={() => { setChatText(prompt); chatInput.current?.focus(); }}>{prompt}<Icon name="arrow" size={16}/></button>)}</div>}{chatRunning && <div className="assistant-progress"><span className="spinner"/>{liveStatus || "Le coordinateur travaille sur votre demande…"}</div>}<div ref={messageEnd}/></div><form className="chat-composer" onSubmit={event => void sendChat(event)}><div className="chat-context"><span className="context-label">Contexte</span><select aria-label="Portée de la demande au chat" value={wholeSheet ? "sheet" : "selection"} onChange={e => setWholeSheet(e.target.value === "sheet")} disabled={!sheet}><option value="selection">{sheetName ? `${sheetName} · ${scope.range || "A1"}` : "Aucune feuille"}</option><option value="sheet">Toute la feuille</option></select></div>{!cockpit && (wholeSheet || extraSheets.length > 0) && <label className="checkbox-row"><input type="checkbox" checked={allowStructure} onChange={e => setAllowStructure(e.target.checked)}/>Autoriser les changements de structure</label>}{pendingChat && <p className="pending-intent-note">La demande non acquittée sera reprise avec son périmètre enregistré.</p>}<details className="chat-multiscope"><summary>{extraSheets.length ? `${extraSheets.length + 1} feuilles dans le périmètre` : "Consulter ou modifier plusieurs feuilles"}</summary><p>Sélectionnez les feuilles que les agents pourront proposer de modifier.</p>{sheets.filter(s => s.name !== sheetName).map(s => <label key={s.name}><input type="checkbox" checked={extraSheets.includes(s.name)} onChange={e => setExtraSheets(current => e.target.checked ? [...current, s.name] : current.filter(name => name !== s.name))}/>{s.name}</label>)}</details><textarea ref={chatInput} aria-label="Message aux agents" rows={3} placeholder={active ? "Décrivez une hypothèse, posez une question…" : "Sélectionnez un dossier pour commencer"} value={chatText} disabled={!active || chatRunning} onChange={e => { setChatText(e.target.value); localStorage.setItem("tca.chat.draft." + caseId, e.target.value); }} onKeyDown={(event: KeyboardEvent<HTMLTextAreaElement>) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void sendChat(); } }}/><div className="composer-actions"><button type="button" className="icon-button" aria-label="Ajouter une source à la conversation" title="Ajouter une source" disabled={!active} onClick={() => setDialog("source")}><Icon name="plus"/></button><small>Les propositions restent au brouillon</small><button className="send-button" aria-label="Envoyer aux agents" title="Envoyer" disabled={!active || !sheet || !chatText.trim() || chatRunning || busy}><Icon name="arrow"/></button></div></form></> : <><div className="agents-intro"><p>Les rôles sont lus dans le modèle du dossier. Ouvrez une feuille pour donner ce contexte au chat.</p><div className="filter-input"><Icon name="search" size={15}/><input aria-label="Filtrer les agents" placeholder="Rechercher un agent" value={agentFilter} onChange={e => setAgentFilter(e.target.value)}/></div></div><div className="agents-list">{agents.filter(agent => `${agent.sheet} ${agent.role}`.toLowerCase().includes(agentFilter.toLowerCase())).map(agent => <article className={"agent-card " + (agent.sheet === sheetName ? "current" : "")} key={agent.id}><div className="agent-card-heading"><span><Icon name="table" size={17}/></span><strong>{agent.sheet}</strong><small>{agent.id.replace(/^AGENT_?/i, "")}</small></div><p>{agent.role}</p><button className="text-button" onClick={() => { if (cockpit) window.dispatchEvent(new CustomEvent("cockpit:open-agent-sheet", { detail: { name: agent.sheet } })); else { setSheetName(agent.sheet); setPage("forecast"); setGuided(false); setWholeSheet(false); } setRightTab("chat"); chatInput.current?.focus(); }}>Travailler sur cette feuille <Icon name="arrow" size={14}/></button></article>)}</div></>}
        <div className="assistant-footer"><span className="local-dot"/>Service local · fournisseur API configurable<button onClick={() => setDialog("settings")} aria-label="Configurer l’API du chat"><Icon name="settings" size={14}/></button></div>
      </aside>
  </>;
  const toolbar = <>
          <div className="workspace-toolbar"><div className="button-group"><Button icon="refresh" disabled={mutating || !!running.length || hasDraft} title={hasDraft ? "Appliquez ou videz le brouillon avant de recalculer." : "Recalculer dans Excel"} onClick={() => ignore(action("/recalculate", {}, "POST", undefined, "recalculate:" + (active?.revision ?? 0)))}>Recalculer</Button><Button icon="table" onClick={() => void openCharts()}>Graphiques</Button><Button icon="history" onClick={() => setDialog("jobs")}>Tâches</Button></div><label className="evidence-picker">Source de la saisie<select aria-label="Source de la saisie" value={evidence} onChange={e => setEvidence(e.target.value)}><option value="">Saisie directe</option>{sources.map(source => <option key={source.id} value={source.id}>{source.title}</option>)}</select></label></div>
          {running.length > 0 && <div className="jobs-banner" role="status"><span className="spinner"/><span>{liveStatus || running.map(job => `${statusLabel(job.kind)} · ${statusLabel(job.status)}`).join(" — ")}</span></div>}
          {!!unreadErrors.length && <details className="job-errors"><summary><Icon name="info" size={16}/> {unreadErrors.length} tâche(s) à examiner</summary>{unreadErrors.map(job => <div key={job.id}><strong>{statusLabel(job.kind)} · {statusLabel(job.status)}</strong><p>{errorText(job.error || "La tâche n’a pas abouti. Consultez le dossier avant de relancer.")}</p><Button disabled={mutating || !!running.length} onClick={() => ignore(action("/jobs/" + encodeURIComponent(job.id) + "/retry", {}, "POST", undefined, "retry:" + job.id))}>Reprendre cette tâche</Button></div>)}</details>}
  </>;
  const draftBar = <>
          <div className={"draft-bar " + (hasDraft ? "has-changes" : "")}><div className="draft-label"><span className="draft-symbol"><Icon name="file" size={18}/></span><div><strong>Brouillon partagé <span>{draft.operations?.length || 0}</span></strong><small>{draft.conflicts?.length ? `${draft.conflicts.length} conflit(s) à arbitrer` : hasDraft ? statusLabel(draft.status) + " · tableau et chat" : "Les prochaines modifications apparaîtront ici"}</small></div></div><div className="button-group"><Button disabled={!hasDraft || mutating} onClick={() => setDialog("draft")}>Voir le lot</Button><Button icon="search" disabled={!hasDraft || mutating || !!running.length || !!draft.conflicts?.length} onClick={() => { setDialog("draft"); ignore(action("/draft/preview", {})); }}>Aperçu</Button><Button icon="check" className="primary" disabled={!ready || mutating || !!running.length} onClick={() => setDialog("draft")}>Appliquer</Button></div></div>
  </>;
  if (cockpit) return <Suspense fallback={<p role="status">Ouverture du cockpit…</p>}><ConnectedCockpit key={caseId}
    cases={cases} caseId={caseId} active={active} initializing={initializing} connection={connection}
    sources={sources} agents={agents} sheets={sheets} sheetName={sheetName} jobs={jobs} draft={draft}
    refresh={connectedRefresh + gridRefresh + jobs.filter(job => !isRunning(job.status)).length} blocked={mutating}
    error={error} notice={notice} onDismiss={() => { setError(""); setNotice(""); }}
    onRefresh={async () => { await refreshCases(); await refreshCase(); }} onCase={chooseCase}
    onNew={() => setDialog("new")} onSettings={() => setDialog("settings")} onSource={() => setDialog("source")}
    onDraft={() => { if (selectedRef.current === caseId) setDialog("draft"); }} onVersions={() => void openVersions()} onDownload={() => void downloadWorkbook()}
    onJobs={() => setDialog("jobs")} onSheet={selectConnectedSheet}
    onContext={(name, prompt) => { if (name && sheets.some(item => item.name === name)) { setSheetName(name); setScope({ sheet: name, range: "A1" }); setWholeSheet(true); setExtraSheets([]); } if (prompt) setChatText(prompt); setRightOpen(true); setRightTab("chat"); }}
    toolbar={toolbar} draftBar={draftBar} dialogs={dialogs} dialogsOpen={dialog !== null || structure !== null || intentReview !== null} chat={chatPanel}
    workshop={(target, openSheet) => active ? <Suspense fallback={<p role="status">Ouverture du parcours…</p>}><Workshop key={caseId + ":" + target} case={active} page={target} blocked={mutating} refresh={gridRefresh + jobs.filter(job => !isRunning(job.status)).length} sources={sources} onRefresh={refreshCase} onSource={() => setDialog("source")} onDraft={() => { if (selectedRef.current === caseId) setDialog("draft"); }} onCase={chooseCase} onSheet={openSheet}/></Suspense> : null}
    grid={onDiscuss => sheet ? <WorkbookGrid ordinary revision={active?.revision ?? 0} key={caseId + "!" + sheet.name} caseId={caseId} sheet={sheet} draft={draft} refresh={gridRefresh} disabled={mutating} focusCell={gridTarget?.sheet === sheet.name ? gridTarget.cell : undefined} onDiscuss={() => { setRightOpen(true); setRightTab("chat"); setWholeSheet(false); setExtraSheets([]); onDiscuss(); }} onEdit={edit} onScope={updateScope} onStructural={() => setError("Les changements de structure nécessitent l’atelier de maintenance du modèle. Le cockpit conserve les formules et n’édite que les entrées métier reconnues.")}/> : <Empty icon="table" title="Aucune feuille disponible"><p>Choisissez une feuille du dossier.</p></Empty>}
  /></Suspense>;

  return <div className="app-shell">
    <header className="app-header"><a className="brand" href="#" onClick={event => event.preventDefault()} aria-label="TCA Atelier Business Plan"><span className="brand-mark"><i/><i/><i/><i/></span><span>TCA<span className="brand-divider">/</span><span className="brand-product">Atelier BP</span></span></a><div className="header-center"><span className="local-dot"/>Espace de travail local</div><div className="header-actions"><button className="header-icon" title="Afficher ou masquer la navigation" aria-label="Afficher ou masquer la navigation" onClick={() => setLeftOpen(value => !value)}><Icon name="panel"/></button><button className="header-icon" title="Afficher ou masquer le chat" aria-label="Afficher ou masquer le chat" onClick={() => setRightOpen(value => !value)}><Icon name="chat"/></button><button className="header-icon" title="Réglages API" aria-label="Réglages API" onClick={() => setDialog("settings")}><Icon name="settings"/></button><span className="avatar">TC</span></div></header>
    {(error || notice) && <div className={"global-message " + (error ? "error" : "success")} role={error ? "alert" : "status"}><Icon name={error ? "info" : "check"}/><span>{error || notice}</span>{error && <button onClick={() => { setError(""); void refreshCases(); void refreshCase(); }}>Actualiser</button>}<button className="icon-button" aria-label="Fermer le message" onClick={() => { setError(""); setNotice(""); }}><Icon name="close" size={16}/></button></div>}
    <div className="workspace-layout" style={layout}>
      <aside className={"left-panel " + (!leftOpen ? "collapsed" : "")} aria-label="Dossiers et ressources"><div className="section-heading"><span>DOSSIERS</span><button className="icon-button" title="Nouveau dossier" aria-label="Nouveau dossier" onClick={() => setDialog("new")}><Icon name="plus"/></button></div><div className="case-list">{cases.length ? cases.map(item => <button key={item.id} className={"case-item " + (item.id === caseId ? "selected" : "")} onClick={() => chooseCase(item.id)}><span className="case-icon"><Icon name="folder" size={19}/></span><span><strong>{item.name}</strong><small>{item.client_name || "Dossier local"}</small></span>{item.id === caseId && <span className="selected-dot"/>}</button>) : <p className="left-note">{initializing ? "Chargement…" : "Créez votre premier dossier."}</p>}</div>
        <div className="left-tabs"><button className={leftTab === "sheets" ? "active" : ""} onClick={() => setLeftTab("sheets")}>Feuilles <span>{sheets.length}</span></button><button className={leftTab === "sources" ? "active" : ""} onClick={() => setLeftTab("sources")}>Sources <span>{sources.length}</span></button></div>
        {leftTab === "sheets" ? <><div className="filter-input"><Icon name="search" size={15}/><input aria-label="Filtrer les feuilles" placeholder="Rechercher une feuille" value={sheetFilter} onChange={e => setSheetFilter(e.target.value)}/></div><nav className="sheet-list" aria-label="Feuilles du classeur">{sheets.filter(item => item.name.toLocaleLowerCase("fr").includes(sheetFilter.toLocaleLowerCase("fr"))).map((item, index) => <button className={"sheet-item " + (item.name === sheetName ? "selected" : "")} key={item.name} onClick={() => { setSheetName(item.name); setWholeSheet(false); setPage("forecast"); setGuided(false); }}><Icon name="table" size={16}/><span>{item.name}</span><small>{String(index + 1).padStart(2, "0")}</small></button>)}</nav><div className="left-footer"><Button icon="plus" disabled={!active || mutating} onClick={() => setStructure({ kind: "add_sheet", index: 0 })}>Nouvelle feuille</Button></div></> : <><div className="sources-header"><p>Pièces et réponses du dossier</p><Button icon="plus" disabled={!active} onClick={() => setDialog("source")}>Ajouter une source</Button></div><div className="sources-list">{sources.length ? sources.map(source => <div className="source-card" key={source.id}><span className="source-icon"><Icon name="file"/></span><div><strong>{source.title}</strong><small>{source.kind || "Document"} {dateText(source.created_at) && "· " + dateText(source.created_at)}</small></div></div>) : <Empty icon="file" title="Vos sources, au même endroit"><p>Ajoutez des documents ou vos réponses métier.</p></Empty>}</div></>}
        <div className="connection-state"><span className={"connection-dot " + connection}/>{!caseId ? "Aucun dossier sélectionné" : connection === "connected" ? "Synchronisé avec le serveur" : connection === "retrying" ? "Reconnexion au serveur…" : "Connexion au serveur…"}</div>
      </aside>
      {leftOpen ? <ResizeHandle side="left" value={leftWidth} change={setLeftWidth}/> : <div/>}
      <main className="main-panel">
        {active ? <><div className="project-heading"><div><div className="eyebrow">{active.client_name || "DOSSIER LOCAL"}</div><h1>{active.name}</h1><div className="project-meta"><span className="badge">Révision {active.revision ?? 0}</span><span className={"badge " + (active.calculation_status === "RECALCULE" ? "good" : "warning")}>{statusLabel(active.calculation_status)}</span></div></div><div className="project-actions"><Button icon="history" onClick={() => void openVersions()} title="Historique des versions" aria-label="Historique des versions"/><Button icon="download" onClick={() => void downloadWorkbook()}>Classeur</Button></div></div>
          {toolbar}
          <nav className="workshop-nav" aria-label="Étapes du dossier">{workshopPages.map(item => <button key={item.id} className={page === item.id ? "active" : ""} aria-current={page === item.id ? "step" : undefined} onClick={() => setPage(item.id)}>{item.label}</button>)}</nav>
          {page === "forecast" && <div className="forecast-switch"><button className={!guided ? "active" : ""} onClick={() => setGuided(false)}>Tableur</button><button className={guided ? "active" : ""} onClick={() => setGuided(true)}>Hypothèses guidées</button><span>Le chat et le brouillon restent communs.</span></div>}
          {(page !== "forecast" || guided) && <Suspense fallback={<div className="workshop-page"><p>Ouverture du parcours…</p></div>}><Workshop key={caseId + ":" + page} case={active} page={page} blocked={mutating} refresh={gridRefresh + jobs.filter(job => !isRunning(job.status)).length} sources={sources} onRefresh={refreshCase} onSource={() => setDialog("source")} onDraft={() => { if (selectedRef.current === caseId) setDialog("draft"); }} onCase={chooseCase} onSheet={(name, cell) => { setSheetName(name); setPage("forecast"); setGuided(false); if (cell) { setScope({ sheet: name, range: cell }); setGridTarget({ sheet: name, cell }); } }}/ ></Suspense>}
          {page === "forecast" && !guided && (sheet ? <WorkbookGrid key={caseId + "!" + sheet.name} caseId={caseId} sheet={sheet} draft={draft} refresh={gridRefresh} disabled={mutating} focusCell={gridTarget?.sheet === sheet.name ? gridTarget.cell : undefined} onDiscuss={() => { setRightOpen(true); setRightTab("chat"); setWholeSheet(false); setExtraSheets([]); chatInput.current?.focus(); }} onEdit={edit} onScope={updateScope} onStructural={(kind, index) => setStructure({ kind, index })}/> : <Empty icon="table" title="Aucune feuille disponible"><p>Les feuilles du classeur apparaîtront ici.</p></Empty>)}
          {draftBar}
        </> : initializing || caseId ? <div className="workspace-welcome"><span className="spinner"/><h2>Ouverture du dossier…</h2><p>Le serveur prépare les informations du classeur.</p></div> : <div className="workspace-welcome"><div className="welcome-art"><span/><span/><span/><Icon name="table" size={54}/></div><p className="eyebrow">VOTRE ATELIER BUSINESS PLAN</p><h1>Du dossier au modèle,<br/>un même espace de travail.</h1><p>Rassemblez vos sources, construisez le prévisionnel<br/>et préparez les évolutions avec les agents.</p><Button className="primary large" icon="plus" onClick={() => setDialog("new")}>Créer un premier dossier</Button><button className="text-button" onClick={() => setDialog("settings")}>Configurer le chat</button></div>}
      </main>
      {rightOpen ? <ResizeHandle side="right" value={rightWidth} change={setRightWidth}/> : <div/>}
      {chatPanel}
    </div>
    {dialogs}
  </div>;
}
type FormEventLike = { preventDefault: () => void };
