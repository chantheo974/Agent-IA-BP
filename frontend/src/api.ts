export class ApiError extends Error {
  constructor(message: string, public status: number, public detail?: unknown) { super(message); }
}
export function errorText(value: unknown): string {
  if (value instanceof Error) return value.message;
  if (typeof value === "string") return value;
  if (value && typeof value === "object") {
    const object = value as Record<string, unknown>;
    for (const key of ["message", "reason", "detail", "error"]) if (object[key] != null) return errorText(object[key]);
    return JSON.stringify(value);
  }
  return "Une erreur est survenue. Réessayez après vérification du dossier.";
}
export async function api<T>(path: string, method = "GET", body?: unknown, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch("/api" + path, { method, signal, credentials: "same-origin", headers: body instanceof FormData ? undefined : { "Content-Type": "application/json" }, body: body == null ? undefined : body instanceof FormData ? body : JSON.stringify(body) });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError("Le serveur local est injoignable. Vérifiez qu’il est démarré.", 0, error);
  }
  let text: string;
  try { text = await response.text(); }
  catch (error) { throw new ApiError("La réponse du serveur a été interrompue. Votre demande est conservée pour sa reprise.", 0, error); }
  let data: unknown = null;
  try { data = text ? JSON.parse(text) : null; } catch { if (response.ok) throw new ApiError("La réponse est illisible. Votre demande est conservée pour sa reprise.", 0); }
  if (!response.ok) throw new ApiError(data ? errorText(data) : `La requête a échoué (${response.status}).`, response.status, data);
  return data as T;
}
export const casePath = (id: string) => "/cases/" + encodeURIComponent(id);
export const requestId = () => crypto.randomUUID();
export type IntentReviewRequest = { caseId: string; requestId: string; key: string; path: string };

function canonical(value: unknown): string {
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (value && typeof value === "object") return "{" + Object.entries(value).filter(([, v]) => v !== undefined).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => JSON.stringify(k) + ":" + canonical(v)).join(",") + "}";
  return JSON.stringify(value) ?? "null";
}
async function withIntent<T>(caseId: string, path: string, method: string, body: unknown, send: (id: string) => Promise<T>): Promise<T> {
  const bytes = new TextEncoder().encode(canonical({ caseId, path, method, body }));
  const digest = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map(n => n.toString(16).padStart(2, "0")).join("");
  const key = "tca.intent.v1." + caseId + "." + digest;
  // Each intention occupies its own key: success in another case cannot erase it.
  const existing = localStorage.getItem(key), id = existing || requestId();
  localStorage.setItem(key, id);
  try {
    if (existing) {
      try {
        const previous = await api<{ found: boolean; result?: T; message?: string }>(casePath(caseId) + "/intents/" + encodeURIComponent(id));
        if (previous.found && previous.result != null) { localStorage.removeItem(key); return previous.result; }
        if (previous.found) throw new ApiError(previous.message || "Cette demande est conservée sans résultat acquitté. Examinez l’état du dossier avant une nouvelle écriture.", 409, { review_required: true });
      } catch (error) { if (!(error instanceof ApiError && error.status === 404)) throw error; }
    }
    const result = await send(id);
    localStorage.removeItem(key);
    return result;
  } catch (error) {
    const review = error instanceof ApiError && JSON.stringify(error.detail || {}).includes('"review_required":true');
    if (review) window.dispatchEvent(new CustomEvent<IntentReviewRequest>("tca-intent-review", { detail: { caseId, requestId: id, key, path } }));
    if (!review && error instanceof ApiError && error.status >= 400 && error.status < 500 && ![408, 429].includes(error.status)) localStorage.removeItem(key);
    throw error;
  }
}
export function intentApi<T>(caseId: string, path: string, method = "POST", body: Record<string, unknown> = {}): Promise<T> {
  return withIntent(caseId, path, method, body, id => api<T>(casePath(caseId) + path, method, { ...body, request_id: id }));
}
export async function intentUpload<T>(caseId: string, path: string, body: FormData): Promise<T> {
  const identity: Record<string, unknown> = {};
  for (const [key, value] of body.entries()) {
    if (key === "request_id") continue;
    if (value instanceof File) {
      const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", await value.arrayBuffer()))].map(n => n.toString(16).padStart(2, "0")).join("");
      identity[key] = { name: value.name, size: value.size, sha256: hash };
    } else identity[key] = value;
  }
  return withIntent(caseId, path, "POST", identity, id => { body.set("request_id", id); return api<T>(casePath(caseId) + path, "POST", body); });
}

export function columnName(column: number): string {
  let result = "";
  for (let n = column; n > 0; n = Math.floor((n - 1) / 26)) result = String.fromCharCode(65 + (n - 1) % 26) + result;
  return result;
}
export function parseAddress(text: string): [number, number] | null {
  const match = /^\$?([A-Z]{1,3})\$?([1-9]\d*)$/i.exec(text.trim());
  if (!match) return null;
  const column = [...match[1].toUpperCase()].reduce((n, char) => n * 26 + char.charCodeAt(0) - 64, 0);
  const row = Number(match[2]);
  return column <= 16384 && row <= 1048576 ? [column - 1, row - 1] : null;
}
export type NumericLocale = "fr" | "en";
export function parseValue(text: string, locale?: NumericLocale): string | number | boolean | null {
  const trimmed = text.trim();
  if (!trimmed) return null;
  if (/^(VRAI|TRUE)$/i.test(trimmed)) return true;
  if (/^(FAUX|FALSE)$/i.test(trimmed)) return false;
  const date = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(trimmed);
  if (date) {
    const day = Number(date[1]), month = Number(date[2]), year = Number(date[3]);
    const parsed = new Date(0); parsed.setUTCHours(0, 0, 0, 0); parsed.setUTCFullYear(year, month - 1, day);
    if (year > 0 && parsed.getUTCFullYear() === year && parsed.getUTCMonth() === month - 1 && parsed.getUTCDate() === day)
      return `${date[3]}-${date[2].padStart(2, "0")}-${date[1].padStart(2, "0")}`;
    return text;
  }
  let numeric = trimmed.replace(/\u00a0|\u202f/g, "");
  if (locale === "fr") {
    if (/^[+-]?\d{1,3}(?: \d{3})+(?:,\d+)?%?$/.test(numeric)) numeric = numeric.replaceAll(" ", "");
    if (numeric.includes(".") && !/[eE]/.test(numeric)) return text;
  }
  if (locale === "en") {
    if (/^[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?$/.test(numeric)) numeric = numeric.replaceAll(",", "");
    else if (numeric.includes(",")) return text;
  }
  if (/^[+-]?(?:0|[1-9]\d*)(?:[.,]\d+)?(?:[eE][+-]?\d+)?%?$/.test(numeric)) {
    const canonicalNumber = numeric.replace(",", ".").replace(/%$/, "");
    const significant = canonicalNumber.split(/[eE]/)[0].replace(/[+\-.]/g, "").replace(/^0+/, "");
    const raw = Number(canonicalNumber);
    // Excel retains fifteen significant digits; keep longer identifiers and
    // amounts as text instead of rounding them during a paste or a form entry.
    if (significant.length > 15 || (Number.isInteger(raw) && !Number.isSafeInteger(raw))) return text;
    const number = raw / (numeric.endsWith("%") ? 100 : 1);
    if (Number.isFinite(number)) return number;
  }
  return text;
}
export async function downloadFile(path: string, fallback: string): Promise<void> {
  let response: Response;
  try { response = await fetch("/api" + path, { credentials: "same-origin" }); }
  catch (error) { throw new ApiError("Le serveur local est injoignable. Vérifiez qu’il est démarré.", 0, error); }
  if (!response.ok) {
    let detail: unknown;
    try { detail = await response.json(); } catch { /* Preserve a readable HTTP error. */ }
    throw new ApiError(detail ? errorText(detail) : `Le téléchargement a échoué (${response.status}).`, response.status, detail);
  }
  const blob = await response.blob(), url = URL.createObjectURL(blob), link = document.createElement("a");
  const disposition = response.headers.get("content-disposition") || "";
  const encoded = /filename\*=UTF-8''([^;]+)/i.exec(disposition)?.[1], plain = /filename="?([^";]+)"?/i.exec(disposition)?.[1];
  let filename = plain || fallback;
  if (encoded) { try { filename = decodeURIComponent(encoded); } catch { /* Use the plain safe fallback. */ } }
  link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}
export function displayValue(value: unknown): string {
  if (value == null) return "";
  if (value === true) return "VRAI";
  if (value === false) return "FAUX";
  return String(value);
}
export const isRunning = (status?: string) => status === "QUEUED" || status === "RUNNING";
export function statusLabel(status?: string) {
  const operations: Record<string, string> = { pending: "Résultat non acquitté", review_required: "État à examiner", reviewed: "Examinée", profile: "Profil", answers: "Réponses guidées", "actuals/import": "Import du réalisé", "actuals/apply": "Validation du réalisé", "capitalization/apply": "Validation de la capitalisation", "draft/operations": "Préparation du brouillon", preview: "Aperçu", apply: "Application", recalculate: "Recalcul", chat: "Conversation", restore: "Restauration", solve_wacc: "Calcul du WACC", verify_sensitivity: "Vérification des sensibilités", decision_extract: "Extraction de document", decision_report: "Génération des livrables", decision_goal: "Recherche d’objectif", decision_sensitivity: "Campagne de sensibilité", converged: "Objectif atteint dans la tolérance", unbracketed: "Cible hors de l’intervalle évalué", discrete_target_unreachable: "Cible inaccessible avec les valeurs entières voisines", non_monotonic: "Réponse non monotone : examiner les essais", budget_exhausted: "Nombre maximal d’évaluations atteint", lever_tolerance_reached: "Précision maximale du levier atteinte", a_completer_ou_recalculer: "À compléter ou recalculer", calcule: "Calculé", raccord_a_valider: "Raccord à valider", a_calculer_dans_excel: "À calculer dans Excel", confirme: "Confirmé", a_confirmer: "À confirmer", cancelled: "Interrompu à votre demande" };
  if (status && operations[status.toLowerCase()]) return operations[status.toLowerCase()];
  const labels: Record<string, string> = { QUEUED: "En attente", RUNNING: "En cours", SUCCEEDED: "Terminé", FAILED: "Échec", INTERRUPTED: "Interrompu", RECALCULE: "Recalculé", A_RECALCULER: "À recalculer", NON_RENSEIGNE: "À renseigner", PRET_A_APPLIQUER: "Prêt à appliquer", PREVIEWED: "Aperçu prêt", READY: "Prêt", CONFLICT: "À arbitrer", CONFLICTS: "À arbitrer", EMPTY: "Aucun changement", DIRTY: "À vérifier", DRAFT: "Brouillon", APPLIED: "Appliqué" };
  return status ? labels[status] || status.replaceAll("_", " ").toLowerCase() : "Non renseigné";
}
