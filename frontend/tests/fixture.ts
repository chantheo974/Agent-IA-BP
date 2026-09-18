import type { Page } from "@playwright/test";
import type { Draft, Job, Message, Operation, Source } from "../src/types";

export async function mockWorkspace(page: Page) {
  const state = {
    case: { id: "demo-ui", client_name: "Organisation de test", name: "Développement · recette interface", revision: 0, calculation_status: "A_RECALCULER" },
    sources: [{ id: "source-1", title: "Hypothèses de recette", kind: "Texte" }] as Source[],
    draft: { id: "draft-1", revision: 0, status: "EMPTY", operations: [], changes: [], conflicts: [] } as Draft,
    jobs: [] as Job[], messages: [] as Message[],
    requests: [] as { path: string; method: string; body: any }[],
    settings: { base_url: "https://provider.example.test", model: "test-model", api_key_configured: false, models: ["test-model"] },
  };
  await page.route("**/api/**", async route => {
    const req = route.request(), url = new URL(req.url()), path = url.pathname.replace("/api", ""), method = req.method();
    const body = req.postData() && req.headers()["content-type"]?.includes("application/json") ? req.postDataJSON() : null;
    state.requests.push({ path, method, body });
    let data: unknown;
    if (path.endsWith("/events")) return route.fulfill({ contentType: "text/event-stream", body: ": fixture browser only\n\n" });
    if (path === "/settings") {
      if (method === "PUT") state.settings = { ...state.settings, base_url: body.base_url, model: body.model, api_key_configured: !!body.api_key || state.settings.api_key_configured };
      data = state.settings;
    } else if (path === "/settings/test") data = { ok: true, model_available: true };
    else if (path === "/cases") data = method === "POST" ? state.case : { cases: [state.case] };
    else if (path === "/cases/demo-ui") data = state.case;
    else if (path.endsWith("/sheets")) data = { sheets: [{ name: "Control", rows: 1000, columns: 40 }, { name: "Compte de résultat", rows: 120, columns: 30 }] };
    else if (path.endsWith("/cells")) {
      data = { revision: state.case.revision, cells: [{ cell: "A1", row: 1, column: 1, value: "Hypothèses de travail", display: "Hypothèses de travail" }, { cell: "B10", row: 10, column: 2, value: "Année de départ", display: "Année de départ" }, { cell: "C10", row: 10, column: 3, value: 2026, display: "2026", state: "HYPOTHESE", format: "0" }] };
    } else if (path.endsWith("/sources")) {
      if (method === "POST") state.sources.push({ id: "source-" + (state.sources.length + 1), title: body.title, kind: "Texte" });
      data = method === "POST" ? state.sources.at(-1) : { sources: state.sources };
    } else if (path.endsWith("/agents")) data = { agents: [{ id: "agent-control", sheet: "Control", role: "Coordonner le calendrier et les hypothèses du dossier." }, { id: "agent-cr", sheet: "Compte de résultat", role: "Expliquer les produits et charges." }] };
    else if (path.endsWith("/qualifications")) data = { modules: [], declarations: [], questions: [] };
    else if (path.endsWith("/draft/operations")) {
      for (const op of body.operations as Operation[]) {
        state.draft.operations = (state.draft.operations || []).filter(old => !(old.type === op.type && old.sheet === op.sheet && old.cell === op.cell));
        state.draft.operations.push(op);
      }
      state.draft.status = "DRAFT"; state.draft.changes = []; data = state.draft;
    } else if (path.endsWith("/draft/preview")) {
      state.draft.status = "READY"; state.draft.approval_token = "reviewed-preview-token";
      state.draft.changes = state.draft.operations?.map(op => ({ ...op, before: { value: 2026, formula: null }, after: { value: op.value ?? null, formula: op.formula ?? null } }));
      const job = { id: "preview-1", kind: "preview", status: "SUCCEEDED" }; state.jobs.push(job); data = { job };
    } else if (path.endsWith("/draft/apply")) {
      state.case.revision++; state.draft = { status: "APPLIED", operations: [], changes: [], conflicts: [] };
      const job = { id: "apply-1", kind: "apply", status: "SUCCEEDED" }; state.jobs.push(job); data = { job };
    } else if (path.endsWith("/draft/resolve")) { state.draft.conflicts = []; state.draft.status = "DRAFT"; data = state.draft; }
    else if (path.endsWith("/draft")) {
      if (method === "DELETE") state.draft = { status: "EMPTY", operations: [], changes: [], conflicts: [] };
      data = state.draft;
    } else if (path.endsWith("/chat")) {
      if (method === "POST") {
        state.messages.push({ id: "user-1", role: "user", content: body.message });
        const job = { id: "chat-1", kind: "chat", status: "FAILED", error: { message: "Fournisseur fictif : connexion indisponible." } };
        state.jobs.push(job); data = { job };
      } else data = { messages: state.messages };
    } else if (path.endsWith("/retry")) { const job = { id: "retry-1", kind: "chat", status: "QUEUED" }; state.jobs.push(job); data = { job }; }
    else if (path.endsWith("/jobs")) data = { jobs: state.jobs };
    else if (path.endsWith("/versions")) data = { versions: [{ id: "v0", revision: 0, kind: "CREATE", current: true }] };
    else if (path.endsWith("/charts")) data = { revision: 0, calculation_status: "A_RECALCULER", charts: [{ name: "Recette", title: "Chiffre d’affaires · valeurs fictives", series: [{ name: "Scénario de test", categories: [2026, 2027, 2028], values: [120, null, 350] }] }] };
    else return route.fulfill({ status: 404, json: { message: "Route non couverte par la fixture : " + path } });
    return route.fulfill({ json: data });
  });
  return state;
}
