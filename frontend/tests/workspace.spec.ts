import { test, expect } from "@playwright/test";
import { mockWorkspace } from "./fixture";
import { parseAddress, parseValue, columnName } from "../src/api";
import { chartLine } from "../src/Dialogs";

test("conversion de saisies : nombres français, pourcentages, formules et identifiants", () => {
  expect(parseValue("12,5%")).toBe(.125); expect(parseValue("0012")).toBe("0012");
  expect(parseValue("VRAI")).toBe(true); expect(parseValue("")).toBe(null);
  expect(parseAddress("$XFD$1048576")).toEqual([16383, 1048575]); expect(parseAddress("XFE1")).toBeNull();
  expect(columnName(703)).toBe("AAA"); expect(parseValue("=SUM(A1:A3)")).toBe("=SUM(A1:A3)");
  expect(parseValue("29/02/2028")).toBe("2028-02-29"); expect(parseValue("29/02/2027")).toBe("29/02/2027");
  expect(parseValue("31/04/2027")).toBe("31/04/2027"); expect(parseValue("01/01/2027")).toBe("2027-01-01");
  expect(chartLine([120, null, 350], 0, 350, 3).match(/M/g)).toHaveLength(2);
  expect(chartLine([120, null, 350], 0, 350, 3)).not.toContain("L");
});

test("source, saisie, aperçu avant/après et application explicitement déclenchée", async ({ page }, testInfo) => {
  const state = await mockWorkspace(page), errors: string[] = []; page.on("pageerror", error => errors.push(error.message));
  await page.goto("/atelier"); await expect(page.getByRole("heading", { name: state.case.name })).toBeVisible();
  await page.getByRole("button", { name: "Sources 1", exact: true }).click();
  await page.getByRole("button", { name: "Ajouter une source", exact: true }).click();
  await page.getByLabel("Titre", { exact: true }).fill("Décision calendrier");
  await page.getByLabel("Contenu", { exact: true }).fill("Début en 2027, information fictive de recette.");
  await page.getByRole("button", { name: "Ajouter la source", exact: true }).click();
  await expect(page.getByText("Décision calendrier", { exact: true }).first()).toBeVisible();
  await page.getByLabel("Source de la saisie").selectOption("source-2");
  await page.getByLabel("Adresse de cellule").fill("C10"); await page.getByLabel("Adresse de cellule").press("Enter");
  await expect(page.getByLabel("Valeur ou formule de la cellule")).toHaveValue("2026");
  await page.getByLabel("Valeur ou formule de la cellule").fill("2027");
  await page.getByRole("button", { name: "Ajouter la valeur au brouillon" }).click();
  await expect.poll(() => state.draft.operations?.length).toBe(1);
  expect(state.draft.operations?.[0]).toMatchObject({ type: "set_value", sheet: "Control", cell: "C10", value: 2027, evidence_id: "source-2" });
  expect(state.requests.some(r => r.path.endsWith("/draft/apply"))).toBe(false);
  await expect(page.getByRole("button", { name: "Appliquer", exact: true })).toBeDisabled();
  await page.getByRole("button", { name: "Aperçu", exact: true }).click();
  const table = page.getByRole("table", { name: "Aperçu des modifications avant et après" });
  await expect(table).toBeVisible(); await expect(table.getByRole("cell", { name: "2026", exact: true })).toBeVisible(); await expect(table.getByRole("cell", { name: "2027", exact: true })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("apercu-avant-apres.png"), fullPage: true });
  await page.getByRole("button", { name: "Appliquer en nouvelle version" }).click();
  expect(state.requests.find(request => request.path.endsWith("/draft/apply"))?.body).toMatchObject({ draft_id: "draft-1", approval_token: "reviewed-preview-token", request_id: expect.any(String) });
  await expect(page.getByText("Révision 1", { exact: true })).toBeVisible(); expect(errors).toEqual([]);
});

test("conflits bloquants, structure explicite et reprise de tâche avec son contexte", async ({ page }) => {
  const state = await mockWorkspace(page);
  state.draft = { status: "BLOCKED", operations: [{ type: "set_value", sheet: "Control", cell: "C10", value: 2027 }], conflicts: [{ index: 0, existing: { value: 2027 }, incoming: { value: 2028 } }] };
  state.jobs = [{ id: "failed-1", kind: "chat", status: "INTERRUPTED", error: "La tâche a été interrompue." }];
  await page.goto("/atelier"); await page.getByRole("button", { name: "Voir le lot" }).click();
  await expect(page.getByRole("button", { name: "Appliquer en nouvelle version" })).toBeDisabled();
  await page.getByRole("button", { name: "Conserver cette proposition" }).click();
  await expect(page.getByText("Décisions à prendre")).toHaveCount(0);
  expect(state.requests.find(r => r.path.endsWith("/draft/resolve"))?.body).toEqual({ index: 0, choice: "existing" });
  await page.getByRole("button", { name: "Fermer", exact: true }).click();
  await page.getByRole("button", { name: "Tâches", exact: true }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Reprendre cette tâche" }).click();
  await expect.poll(() => state.requests.find(r => r.path.endsWith("/jobs/failed-1/retry"))?.body.request_id).toBeTruthy();
});

test("chat réel côté interface : demande bornée et erreur serveur sans réponse inventée", async ({ page }, testInfo) => {
  const state = await mockWorkspace(page); await page.goto("/atelier");
  await page.getByLabel("Adresse de cellule").fill("C10"); await page.getByLabel("Adresse de cellule").press("Enter");
  await page.getByLabel("Message aux agents").fill("Explique le calendrier, sans le modifier.");
  await page.getByRole("button", { name: "Envoyer aux agents" }).click();
  await expect(page.getByText("Explique le calendrier, sans le modifier.", { exact: true })).toBeVisible();
  expect(state.requests.find(r => r.path.endsWith("/chat") && r.method === "POST")?.body.selection).toEqual({ sheet: "Control", range: "C10" });
  await page.locator(".job-errors summary").click();
  await expect(page.getByText("Fournisseur fictif : connexion indisponible.")).toBeVisible();
  expect(state.messages.filter(message => message.role === "assistant")).toHaveLength(0);
  const separator = page.getByRole("separator", { name: "Largeur du panneau de navigation" }); await separator.focus(); await separator.press("ArrowRight"); await expect(separator).toHaveAttribute("aria-valuenow", "280");
  await page.screenshot({ path: testInfo.outputPath("atelier-trois-panneaux.png"), fullPage: true });
});

test("chat multifeuilles : conserver la sélection primaire jusqu’au choix explicite de toute la feuille", async ({ page }) => {
  const state = await mockWorkspace(page); await page.goto("/atelier");
  await page.getByLabel("Adresse de cellule").fill("C10"); await page.getByLabel("Adresse de cellule").press("Enter");
  await page.getByText("Consulter ou modifier plusieurs feuilles", { exact: true }).click();
  await page.getByRole("checkbox", { name: "Compte de résultat", exact: true }).check();
  await expect(page.getByLabel("Portée de la demande au chat")).toHaveValue("selection");
  await page.getByLabel("Message aux agents").fill("Explique cette cellule et ses conséquences sur le résultat.");
  await page.getByRole("button", { name: "Envoyer aux agents" }).click();
  await expect.poll(() => state.requests.filter(r => r.path.endsWith("/chat") && r.method === "POST").length).toBe(1);
  expect(state.requests.find(r => r.path.endsWith("/chat") && r.method === "POST")?.body.selection).toEqual({ sheet: "Control", range: "C10", sheets: ["Control", "Compte de résultat"], allow_structure: false });
  await expect(page.getByLabel("Message aux agents")).toHaveValue("");
  await page.getByLabel("Portée de la demande au chat").selectOption("sheet");
  await page.getByLabel("Message aux agents").fill("Explique maintenant toute la feuille et le résultat.");
  await page.getByRole("button", { name: "Envoyer aux agents" }).click();
  await expect.poll(() => state.requests.filter(r => r.path.endsWith("/chat") && r.method === "POST").length).toBe(2);
  expect(state.requests.filter(r => r.path.endsWith("/chat") && r.method === "POST")[1].body.selection).toEqual({ sheet: "Control", sheets: ["Control", "Compte de résultat"], allow_structure: false });
});

test("réglages API sauvegardés et graphiques accompagnés du statut de calcul", async ({ page }) => {
  const state = await mockWorkspace(page); await page.goto("/atelier");
  await page.getByRole("button", { name: "Réglages API", exact: true }).click();
  await page.getByLabel("Clé API", { exact: false }).fill("fictitious-browser-test-key");
  await page.getByRole("button", { name: "Enregistrer", exact: true }).click();
  await expect(page.getByText("Configuration enregistrée sur ce poste.")).toBeVisible();
  await expect(page.getByLabel("Clé API", { exact: false })).toHaveValue("");
  await page.getByRole("button", { name: "Tester la configuration enregistrée" }).click();
  await expect(page.getByText("Connexion à la configuration enregistrée réussie.")).toBeVisible();
  const localValues = await page.evaluate(() => Object.values(localStorage).join(" "));
  expect(localValues).not.toContain("fictitious-browser-test-key");
  expect(state.requests.find(r => r.path === "/settings/test")?.body).toEqual({});
  await page.getByRole("button", { name: "Fermer", exact: true }).click();
  await page.getByRole("button", { name: "Graphiques", exact: true }).click();
  await expect(page.getByRole("img", { name: "Chiffre d’affaires · valeurs fictives" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Chiffre d’affaires · valeurs fictives" }).locator("circle")).toHaveCount(2);
  await expect(page.getByRole("dialog").getByText("À recalculer", { exact: true })).toBeVisible();
});

test("une réponse de cellules retardée ne remplace pas une saisie en cours", async ({ page }) => {
  const state = await mockWorkspace(page);
  let release: (() => void) | undefined;
  const barrier = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/**/cells?*", async route => { await barrier; await route.fallback(); });
  await page.goto("/atelier"); await expect(page.getByLabel("Valeur ou formule de la cellule")).toBeVisible();
  await page.getByLabel("Valeur ou formule de la cellule").fill("Ma saisie en cours");
  release!();
  await expect.poll(() => state.requests.some(request => request.path.endsWith("/cells"))).toBe(true);
  await expect(page.locator(".sheet-status").getByText("Prêt", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Valeur ou formule de la cellule")).toHaveValue("Ma saisie en cours");
  await page.getByRole("button", { name: "Ajouter la valeur au brouillon" }).click();
  await expect.poll(() => state.draft.operations?.[0]?.value).toBe("Ma saisie en cours");
});

test("collage rectangulaire, formule et ajout de feuille restent dans le brouillon commun", async ({ page, context }) => {
  const state = await mockWorkspace(page); await context.grantPermissions(["clipboard-read", "clipboard-write"]); await page.goto("/atelier");
  await page.getByLabel("Adresse de cellule").fill("C10"); await page.getByLabel("Adresse de cellule").press("Enter");
  await page.evaluate(() => navigator.clipboard.writeText("10\t20\n30\t=SUM(C10:D10)"));
  await page.getByTestId("data-grid-canvas").focus(); await page.keyboard.press("Control+v");
  await expect(page.getByRole("dialog", { name: "Vérifier le collage" })).toBeVisible();
  expect(state.draft.operations).toHaveLength(0);
  await page.getByRole("button", { name: "Ajouter le collage au brouillon" }).click();
  await expect.poll(() => state.draft.operations?.length).toBe(4);
  expect(state.draft.operations).toEqual(expect.arrayContaining([
    expect.objectContaining({ type: "set_value", cell: "C10", value: 10 }),
    expect.objectContaining({ type: "set_value", cell: "D10", value: 20 }),
    expect.objectContaining({ type: "set_value", cell: "C11", value: 30 }),
    expect.objectContaining({ type: "set_formula", cell: "D11", formula: "=SUM(C10:D10)" }),
  ]));
  const paste = state.requests.find(request => request.path.endsWith("/draft/operations")); expect(paste?.body.scope).toEqual({ sheet: "Control", range: "C10:D11" });
  await page.getByRole("button", { name: "Nouvelle feuille", exact: true }).click();
  await page.getByLabel("Nom de la feuille", { exact: true }).fill("Recette complémentaire"); await page.getByLabel("Rôle métier", { exact: true }).fill("Hypothèses documentées de recette.");
  await page.getByRole("button", { name: "Ajouter au brouillon", exact: true }).click();
  await expect.poll(() => state.draft.operations?.length).toBe(5);
  expect(state.draft.operations?.at(-1)).toMatchObject({ type: "add_sheet", name: "Recette complémentaire", role: "Hypothèses documentées de recette." });
  expect(state.requests.some(request => request.path.endsWith("/draft/preview") || request.path.endsWith("/draft/apply"))).toBe(false);
});

test("un refus de reprise reste lisible dans la fenêtre de tâches", async ({ page }) => {
  const state = await mockWorkspace(page); state.jobs = [{ id: "stale", kind: "chat", status: "INTERRUPTED" }];
  await page.route("**/api/**/jobs/stale/retry", route => route.fulfill({ status: 409, json: { detail: "Le contexte du dossier a changé. Préparez une nouvelle demande." } }));
  await page.goto("/atelier"); await page.getByRole("button", { name: "Tâches", exact: true }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Reprendre cette tâche" }).click();
  await expect(page.getByRole("dialog").getByRole("alert")).toContainText("Le contexte du dossier a changé.");
  expect(state.jobs).toHaveLength(1); expect(state.jobs[0].status).toBe("INTERRUPTED");
});

test("une coupure de transport conserve l’identifiant de demande, un refus du serveur le renouvelle", async ({ page }) => {
  const state = await mockWorkspace(page);
  state.jobs = [{ id: "stale", kind: "chat", status: "INTERRUPTED" }];
  const sent: (string | undefined)[] = [];
  await page.route("**/api/**/jobs/stale/retry", route => {
    sent.push(route.request().postDataJSON()?.request_id);
    if (sent.length === 1) return route.abort("connectionreset");
    if (sent.length === 2) return route.fulfill({ status: 409, json: { detail: "Le dossier a changé. Examinez les versions." } });
    return route.fulfill({ json: { job: { id: "retry-1", kind: "chat", status: "QUEUED" } } });
  });
  await page.goto("/atelier");
  await page.getByRole("button", { name: "Tâches", exact: true }).click();
  const retry = page.getByRole("dialog").getByRole("button", { name: "Reprendre cette tâche" });
  await retry.click();
  await expect(page.getByRole("dialog").getByRole("alert")).toContainText("injoignable");
  await retry.click();
  await expect(page.getByRole("dialog").getByRole("alert")).toContainText("Le dossier a changé.");
  await retry.click();
  await expect.poll(() => sent.length).toBe(3);
  expect(sent.every(id => typeof id === "string" && id.length > 0)).toBe(true);
  // Après une coupure, la reprise garde l’identité de la demande : le serveur
  // reconnaît le doublon au lieu de créer un second travail. Après un refus
  // reçu du serveur, la tentative suivante est bien une demande neuve.
  expect(sent[1]).toBe(sent[0]);
  expect(sent[2]).not.toBe(sent[1]);
});

test("un flux d’événements définitivement fermé est reconstruit et resynchronise le dossier", async ({ page }) => {
  const state = await mockWorkspace(page);
  let attempts = 0, caseReads = 0;
  await page.route("**/api/**/events", route => {
    attempts++;
    if (attempts === 1) return route.fulfill({ status: 503, json: { detail: "Flux indisponible." } });
    state.case.revision = 3;
    return route.fulfill({ contentType: "text/event-stream", body: 'id: 8\nevent: resync\ndata: {"reason":"cursor_expired"}\n\nid: 9\nevent: job\ndata: {"status":"SUCCEEDED"}\n\nevent: refresh\ndata: {}\n\n' });
  });
  await page.route("**/api/cases/demo-ui", route => { caseReads++; return route.fulfill({ json: state.case }); });
  await page.goto("/atelier");
  await expect(page.getByText("Reconnexion", { exact: false })).toBeVisible();
  // Le navigateur abandonne un flux fermé sur erreur HTTP : l’atelier doit le
  // reconstruire lui-même, sinon il reste figé sans jamais se resynchroniser.
  await expect.poll(() => attempts, { timeout: 15000 }).toBeGreaterThan(1);
  await expect(page.getByText("Révision 3", { exact: true })).toBeVisible();
  expect(caseReads).toBeGreaterThan(1);
});
