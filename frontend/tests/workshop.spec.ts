import { expect, test } from "@playwright/test";
import { mockWorkspace } from "./fixture";
import { parseValue } from "../src/api";

test("formats numériques explicites : séparateurs, pourcentages et identifiants", () => {
  expect(parseValue("1,234", "en")).toBe(1234);
  expect(parseValue("1,234", "fr")).toBe(1.234);
  expect(parseValue("1 234,56", "fr")).toBe(1234.56);
  expect(parseValue("1,234.56", "en")).toBe(1234.56);
  expect(parseValue("12,5%", "fr")).toBe(.125);
  expect(parseValue("12,5", "en")).toBe("12,5");
  expect(parseValue("001234", "fr")).toBe("001234");
  expect(parseValue("12345678901234567890", "fr")).toBe("12345678901234567890");
  expect(parseValue("123456789012345,12", "fr")).toBe("123456789012345,12");
  expect(parseValue("9007199254740992", "en")).toBe("9007199254740992");
});

test("parcours : profil persisté, réponses guidées au brouillon et accès au tableur", async ({ page }) => {
  const state = await mockWorkspace(page);
  let profile: Record<string, unknown> = {}, answer: Record<string, unknown> | null = null;
  await page.route("**/api/**/profile", route => { if (route.request().method() === "PUT") profile = route.request().postDataJSON().profile; return route.fulfill({ json: { profile } }); });
  await page.route("**/api/**/questionnaire", route => route.fulfill({ json: { questions: [{ field_id: "calendar", label: "Année de départ", sheet: "Control", cell: "C10", value: 2026, required: true }] } }));
  await page.route("**/api/**/answers", route => { answer = route.request().postDataJSON(); state.draft.operations = [{ type: "set_value", sheet: "Control", cell: "C10", value: 2027 }]; state.draft.status = "DRAFT"; return route.fulfill({ json: state.draft }); });
  await page.goto("/atelier");
  await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await page.getByLabel("Nom de l’entreprise").fill("Entreprise fictive autonome");
  await page.getByLabel("Activité", { exact: true }).selectOption("recurring");
  await page.getByLabel("Horizon du prévisionnel").selectOption("10");
  await page.getByRole("button", { name: "Enregistrer le profil" }).click();
  await expect.poll(() => profile.name).toBe("Entreprise fictive autonome");
  expect(profile.horizon_years).toBe(10);
  await page.reload(); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect(page.getByLabel("Nom de l’entreprise")).toHaveValue("Entreprise fictive autonome");
  await page.getByLabel("Année de départ", { exact: true }).fill("2027");
  await page.getByLabel("Source : Année de départ").selectOption("source-1");
  await page.getByRole("button", { name: "Proposer les réponses au brouillon" }).click();
  await expect(page.getByRole("dialog", { name: "Brouillon partagé" })).toBeVisible();
  expect(answer).toMatchObject({ answers: [{ field_id: "calendar", sheet: "Control", cell: "C10", value: 2027, status: "HYPOTHESE", evidence_id: "source-1" }], request_id: expect.any(String), expected_revision: 0 });
  await page.getByRole("button", { name: "Fermer", exact: true }).click();
  await page.getByRole("button", { name: "Control · C10", exact: true }).click();
  await expect(page.getByLabel("Valeur ou formule de la cellule")).toBeVisible();
  await expect(page.getByLabel("Message aux agents")).toBeVisible();
  expect(state.requests.some(r => r.path.endsWith("/draft/apply"))).toBe(false);
});

test("réponse perdue : une réussite dans un autre dossier et un rechargement gardent l’intention", async ({ page }) => {
  const state = await mockWorkspace(page);
  const other = { ...state.case, id: "other-ui", name: "Autre entreprise" };
  const sent: { id: string; request: string }[] = [];
  await page.route("**/api/cases", route => route.fulfill({ json: { cases: [state.case, other] } }));
  await page.route("**/api/cases/other-ui", route => route.fulfill({ json: other }));
  await page.route("**/api/**/recalculate", route => {
    const id = new URL(route.request().url()).pathname.includes("other-ui") ? "other-ui" : "demo-ui";
    sent.push({ id, request: route.request().postDataJSON().request_id });
    if (id === "demo-ui" && sent.filter(s => s.id === id).length === 1) return route.fulfill({ status: 200, contentType: "application/json", body: "{interrupted" });
    return route.fulfill({ json: { job: { id: "job-" + id, kind: "recalculate", status: "SUCCEEDED" } } });
  });
  await page.route("**/api/**/intents/*", route => route.fulfill({ json: { found: false } }));
  await page.goto("/atelier"); await page.getByRole("button", { name: "Recalculer", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("illisible");
  await page.getByRole("button", { name: "Autre entreprise", exact: false }).click();
  await page.getByRole("button", { name: "Recalculer", exact: true }).click();
  await expect.poll(() => sent.length).toBe(2);
  await page.getByRole("button", { name: state.case.name, exact: false }).click();
  await page.reload(); await page.getByRole("button", { name: "Recalculer", exact: true }).click();
  await expect.poll(() => sent.length).toBe(3);
  expect(sent[2].request).toBe(sent[0].request); expect(sent[1].request).not.toBe(sent[0].request);
});

test("dilution : calculer un aperçu ne vaut pas adoption", async ({ page }) => {
  await mockWorkspace(page); let capitalBody: Record<string, unknown> = {}, adopted = false;
  await page.route("**/api/**/scenarios", route => route.fulfill({ json: { scenarios: [] } }));
  await page.route("**/api/**/scenarios/compare", route => route.fulfill({ json: { scenarios: [] } }));
  await page.route("**/api/**/questionnaire", route => route.fulfill({ json: { questions: [] } }));
  await page.route("**/api/**/capitalization", route => {
    if (route.request().method() === "GET") return route.fulfill({ json: { shareholders: [], rounds: [] } });
    capitalBody = route.request().postDataJSON();
    return route.fulfill({ json: { approval_token: "capital-preview", result: { pre_money: 8000000, post_money: 10000000 }, changes: [] } });
  });
  await page.route("**/api/**/capitalization/apply", route => { adopted = true; expect(route.request().postDataJSON().approval_token).toBe("capital-preview"); return route.fulfill({ json: { ok: true } }); });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByLabel("Associé 1", { exact: true }).fill("Fondatrice");
  await page.getByRole("button", { name: "Ajouter un tour", exact: true }).click();
  await page.getByLabel("Pool salarié cible (%)").fill("10");
  await page.getByRole("button", { name: "Calculer et examiner la dilution" }).click();
  await expect(page.getByRole("dialog", { name: "Aperçu de la capitalisation" })).toBeVisible();
  expect(adopted).toBe(false);
  expect(capitalBody).toMatchObject({ rounds: [{ pre_money: 8000000, investment: 2000000, pool_percent: 10, pool_timing: "before" }] });
  await page.getByRole("button", { name: "Approuver et adopter" }).click();
  await expect.poll(() => adopted).toBe(true);
});

test("deux tours : montrer le pool conservé au-dessus de la cible avant toute adoption", async ({ page }) => {
  const state = await mockWorkspace(page); let body: Record<string, unknown> = {};
  const holder = (percent: string) => [{ name: "Fondatrice", shares: "1000", percent }];
  const result = { initial: { holders: holder("100"), pool_ownership: "0" }, holders: holder("63.636363"), final: { holders: holder("63.636363"), pool_shares: "142.857142" }, rounds: [
    { name: "Tour 1", pre_money: "8000000", investment: "2000000", post_money: "10000000", pool_target: "0.10", pool_timing: "before", after: { holders: holder("70"), pool_ownership: "0.10" }, warnings: [] },
    { name: "Tour 2", pre_money: "10000000", investment: "1000000", post_money: "11000000", pool_target: "0.01", pool_timing: "before", after: { holders: holder("63.636363"), pool_ownership: "0.0909090909" }, warnings: ["POOL_EXISTANT_SUPERIEUR_A_LA_CIBLE_AUCUNE_ANNULATION"] },
  ] };
  await page.route("**/api/**/capitalization", route => {
    if (route.request().method() === "GET") return route.fulfill({ json: { shareholders: [], rounds: [] } });
    body = route.request().postDataJSON(); return route.fulfill({ json: { approval_token: "two-rounds", result, changes: [] } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByLabel("Associé 1", { exact: true }).fill("Fondatrice");
  await page.getByRole("button", { name: "Ajouter un tour", exact: true }).click();
  await page.getByRole("button", { name: "Ajouter un tour", exact: true }).click();
  await page.getByLabel("Pool salarié cible (%)").nth(0).fill("10");
  await page.getByLabel("Pool salarié cible (%)").nth(1).fill("1");
  await page.getByLabel("Valorisation avant investissement (€)").nth(1).fill("10000000");
  await page.getByLabel("Montant levé (€)").nth(1).fill("1000000");
  await page.getByRole("button", { name: "Calculer et examiner la dilution" }).click();
  const dialog = page.getByRole("dialog", { name: "Aperçu de la capitalisation" });
  await expect(dialog.getByRole("alert")).toContainText("aucun titre réservé n’a été annulé");
  await expect(dialog.getByRole("row", { name: /Pool salarié réservé/ })).toContainText("9,0909 %");
  await expect(dialog.getByText("Pool cible après le tour : 1 % · constitution avant le tour.", { exact: true })).toBeVisible();
  expect(body).toMatchObject({ rounds: [{ pool_percent: 10, pool_timing: "before" }, { pool_percent: 1, pool_timing: "before" }] });
  expect(state.requests.some(r => r.path.endsWith("/capitalization/apply"))).toBe(false);
});

test("horizon DCF : préparer dix formules, examiner sans appliquer et conserver un modèle déjà migré", async ({ page }) => {
  const state = await mockWorkspace(page), submitted: Record<string, unknown>[] = [];
  await page.route("**/api/**/model/dcf-calendar", route => {
    submitted.push(route.request().postDataJSON());
    if (submitted.length > 1) return route.fulfill({ json: { status: "ALREADY_MIGRATED" } });
    state.draft.operations = Array.from({ length: 10 }, (_, i) => ({ type: "set_formula", sheet: "Valuation", cell: String.fromCharCode(67 + i) + "15", formula: `IF(${i + 1}<=Control!C59,C14,0)` }));
    state.draft.status = "DRAFT";
    return route.fulfill({ json: state.draft });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByText("Formules de valorisation et horizon", { exact: true }).click();
  await page.getByRole("button", { name: "Adapter la valorisation à l’horizon", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Brouillon partagé" });
  await expect(dialog).toBeVisible();
  expect(submitted[0]).toMatchObject({ expected_revision: 0, request_id: expect.any(String) });
  expect(state.draft.operations).toHaveLength(10);
  await dialog.getByRole("button", { name: "Vérifier l’aperçu", exact: true }).click();
  await expect(dialog.getByRole("button", { name: "Appliquer en nouvelle version", exact: true })).toBeEnabled();
  expect(state.requests.some(r => r.path.endsWith("/draft/apply"))).toBe(false);
  expect(state.case.revision).toBe(0);
  await dialog.getByRole("button", { name: "Fermer", exact: true }).click();
  await page.getByRole("button", { name: "Adapter la valorisation à l’horizon", exact: true }).click();
  await expect(page.getByText("La valorisation est déjà adaptée à l’horizon. Votre brouillon est conservé.", { exact: true })).toBeVisible();
  expect(state.draft.operations).toHaveLength(10);
  expect(submitted[1].request_id).not.toBe(submitted[0].request_id);
  expect(state.requests.some(r => r.path.endsWith("/draft") && r.method === "DELETE")).toBe(false);
});

test("horizon DCF : le refus d’un brouillon occupé garde la saisie courante", async ({ page }) => {
  const state = await mockWorkspace(page);
  state.draft.operations = [{ type: "set_value", sheet: "Control", cell: "C10", value: "2027-01-01" }]; state.draft.status = "DRAFT";
  await page.route("**/api/**/model/dcf-calendar", route => route.fulfill({ status: 409, json: { detail: "Terminez le brouillon courant avant de préparer la migration DCF." } }));
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByText("Formules de valorisation et horizon", { exact: true }).click();
  await page.getByRole("button", { name: "Adapter la valorisation à l’horizon", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Terminez le brouillon courant" })).toBeVisible();
  expect(state.draft.operations).toEqual([{ type: "set_value", sheet: "Control", cell: "C10", value: "2027-01-01" }]);
  expect(state.requests.some(r => r.path.endsWith("/draft/apply") || r.method === "DELETE")).toBe(false);
});

test("horizon fiscal : examiner 56 formules sans adoption, conserver le brouillon déjà migré ou refusé", async ({ page }) => {
  const state = await mockWorkspace(page), submitted: Record<string, unknown>[] = [];
  await page.route("**/api/**/model/fiscal-calendar", route => {
    submitted.push(route.request().postDataJSON());
    if (submitted.length === 2) return route.fulfill({ json: { status: "ALREADY_MIGRATED" } });
    if (submitted.length === 3) return route.fulfill({ status: 409, json: { detail: "Terminez le brouillon courant avant la migration du calendrier fiscal." } });
    state.draft.operations = Array.from({ length: 55 }, (_, i) => ({ type: "set_formula", sheet: "Fiscalite", cell: "D" + (i + 1), formula: "=SUM(IF(A1=2026,B1,0))", evidence_id: "source-1" }));
    state.draft.operations.push({ type: "set_formula", sheet: "KPI Dashboard", cell: "E68", formula: '=IF(COUNTIF(A1:A10,"<0")=0,"",B1)', evidence_id: "source-1" }); state.draft.status = "DRAFT";
    return route.fulfill({ json: state.draft });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByText("Fiscalité, trésorerie et horizon", { exact: true }).click();
  const button = page.getByRole("button", { name: "Adapter fiscalité et trésorerie à l’horizon", exact: true });
  await button.click();
  const dialog = page.getByRole("dialog", { name: "Brouillon partagé" });
  await expect(dialog).toBeVisible();
  expect(submitted[0]).toMatchObject({ expected_revision: 0, request_id: expect.any(String) });
  expect(state.draft.operations).toHaveLength(56);
  await expect(dialog.getByText("KPI Dashboard · E68", { exact: true })).toBeVisible();
  await dialog.getByRole("button", { name: "Vérifier l’aperçu", exact: true }).click();
  await expect(dialog.getByRole("button", { name: "Appliquer en nouvelle version", exact: true })).toBeEnabled();
  await dialog.getByRole("button", { name: "Fermer", exact: true }).click();
  await button.click();
  await expect(page.getByText("La fiscalité et la trésorerie sont déjà adaptées à l’horizon. Votre brouillon est conservé.", { exact: true })).toBeVisible();
  await button.click();
  await expect(page.getByRole("alert").filter({ hasText: "Terminez le brouillon courant" })).toBeVisible();
  expect(state.draft.operations).toHaveLength(56);
  expect(state.case.revision).toBe(0);
  expect(state.requests.some(r => r.path.endsWith("/draft/apply") || r.method === "DELETE")).toBe(false);
});

test("registre : conserver les réponses à compléter et préserver les défauts calculés", async ({ page }) => {
  const state = await mockWorkspace(page), submitted: Record<string, unknown>[] = [];
  await page.route("**/api/**/questionnaire", route => route.fulfill({ json: { questions: [] } }));
  await page.route("**/api/**/registers", route => route.fulfill({ json: { registers: [{ sheet: "Effectifs", first_free_row: 12, can_extend: true, fields: [{ field_id: "name", label: "Intitulé du recrutement", required: true }, { field_id: "salary", label: "Salaire annuel" }, { field_id: "cost", label: "Charges calculées", default: 15000, calculated: true }] }] } }));
  await page.route("**/api/**/registers/Effectifs/records", route => {
    submitted.push(route.request().postDataJSON());
    if (submitted.length === 1) return route.fulfill({ json: { status: "NEEDS_INPUT", questions: [{ question: "Précisez le salaire annuel documenté." }] } });
    state.draft.operations = [{ type: "set_value", sheet: "Effectifs", cell: "B12", value: "Commercial" }]; state.draft.status = "DRAFT";
    return route.fulfill({ json: state.draft });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Hypothèses guidées" }).click();
  await page.getByLabel("Lignes métier supplémentaires").fill("51");
  await expect(page.getByRole("button", { name: "Préparer l’extension du registre" })).toBeDisabled();
  await page.getByLabel("Lignes métier supplémentaires").fill("1.5");
  await expect(page.getByRole("button", { name: "Préparer l’extension du registre" })).toBeDisabled();
  await page.getByLabel("Lignes métier supplémentaires").fill("50");
  await expect(page.getByRole("button", { name: "Préparer l’extension du registre" })).toBeEnabled();
  await page.getByLabel(/Intitulé du recrutement/).fill("Commercial");
  await expect(page.getByLabel(/Charges calculées/)).toHaveAttribute("readonly", "");
  await page.getByLabel("Source de cette opération").selectOption("source-1");
  await page.getByRole("button", { name: "Préparer cette opération au brouillon" }).click();
  await expect(page.getByText("Précisez le salaire annuel documenté.")).toBeVisible();
  await expect(page.getByLabel(/Intitulé du recrutement/)).toHaveValue("Commercial");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByLabel("Salaire annuel", { exact: true }).fill("42000");
  await page.getByRole("button", { name: "Préparer cette opération au brouillon" }).click();
  await expect(page.getByRole("dialog", { name: "Brouillon partagé" })).toBeVisible();
  expect(submitted[1]).toMatchObject({ values: { name: "Commercial", salary: 42000 }, evidence_id: "source-1" });
  expect((submitted[1].values as Record<string, unknown>).cost).toBeUndefined();
});

test("réimport Excel : identifier le fichier par son contenu après coupure et rechargement", async ({ page }) => {
  await mockWorkspace(page); const ids: string[] = [];
  await page.route("**/api/**/reports", route => route.fulfill({ json: { reports: [] } }));
  await page.route("**/api/**/workshop", route => route.fulfill({ json: { storage: { used_bytes: 10, free_bytes: 100 } } }));
  await page.route("**/api/**/intents/*", route => route.fulfill({ json: { found: false } }));
  await page.route("**/api/**/roundtrip", route => {
    const body = route.request().postData() || "";
    ids.push(/name="request_id"\r?\n\r?\n([^\r\n]+)/.exec(body)?.[1] || "");
    if (ids.length === 1) return route.abort("connectionreset");
    return route.fulfill({ json: { status: "DRAFT" } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Livrables", exact: true }).click();
  const file = { name: "retour-fictif.xlsm", mimeType: "application/vnd.ms-excel.sheet.macroEnabled.12", buffer: Buffer.from("fichier-identique-pour-reprise") };
  await page.getByLabel("Classeur exporté puis modifié").setInputFiles(file);
  await page.getByRole("button", { name: "Comparer et préparer les corrections" }).click();
  await expect(page.getByRole("alert")).toContainText("injoignable");
  await page.reload(); await page.getByLabel("Classeur exporté puis modifié").setInputFiles(file);
  await page.getByRole("button", { name: "Comparer et préparer les corrections" }).click();
  await expect.poll(() => ids.length).toBe(2); expect(ids[0]).toBeTruthy(); expect(ids[1]).toBe(ids[0]);
});

test("scénarios : les chiffres en cache périmés ne deviennent pas des résultats courants", async ({ page }) => {
  await mockWorkspace(page);
  await page.route("**/api/**/scenarios", route => route.fulfill({ json: { scenarios: [] } }));
  await page.route("**/api/**/scenarios/compare", route => route.fulfill({ json: { scenarios: [{ id: "stale", name: "Scénario à recalculer", metrics: [{ id: "revenue", label: "Chiffre d’affaires", value: null, cached_value: 987654321, status: "A_COMPLETER_OU_RECALCULER", unit: "€" }, { id: "cash", label: "Trésorerie vérifiée", value: 12345, cached_value: 99999, status: "CALCULE", unit: "€" }, { id: "cash_break_date", label: "Rupture de trésorerie", value: null, status: "CALCULE" }] }] } }));
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByText("Scénario à recalculer", { exact: true }).click();
  const comparison = page.locator("details").filter({ has: page.getByText("Scénario à recalculer", { exact: true }) });
  await expect(comparison).toContainText("Chiffre d’affaires");
  await expect(comparison).toContainText("À compléter ou recalculer");
  await expect(comparison).toContainText("12 345 €");
  await expect(comparison).toContainText("Aucune sur la période");
  await expect(comparison).not.toContainText("987"); await expect(comparison).not.toContainText("99 999");
});

test("comparaison mensuelle : aligner les mois et distinguer manque de donnée et hors période", async ({ page }) => {
  await mockWorkspace(page);
  await page.route("**/api/**/scenarios/compare", route => route.fulfill({ json: { calendars_identical: false, scenarios: [
    { id: "reference", name: "Référence", series: [{ id: "cash", label: "Trésorerie mensuelle", unit: "EUR", categories: ["2026-01", "2026-02", "2026-03"], values: [1000, null, 900] }, { id: "revenue", label: "Chiffre d’affaires mensuel", unit: "EUR", categories: ["2026-01", "2026-02", "2026-03"], values: [10, 20, 30] }] },
    { id: "variant", name: "Scénario décalé", series: [{ id: "cash", label: "Trésorerie mensuelle", unit: "EUR", categories: ["2026-02", "2026-03", "2026-04"], values: [1100, 1200, 1300] }] },
  ] } }));
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  const table = page.getByRole("table", { name: "Comparaison mensuelle : Trésorerie mensuelle", exact: true });
  await expect(table).toBeVisible();
  await expect(table.getByRole("row", { name: /2026-01/ })).toContainText("Hors période");
  await expect(table.getByRole("row", { name: /2026-02/ })).toContainText("À compléter");
  await expect(table.getByRole("row", { name: /2026-03/ }).getByRole("cell")).toHaveText(["900", "1\u202f200"]);
  await expect(table.getByRole("row", { name: /2026-04/ }).getByRole("cell")).toHaveText(["Hors période", "1\u202f300"]);
  await page.getByLabel("Série mensuelle à comparer").selectOption("revenue");
  await expect(page.getByRole("table", { name: "Comparaison mensuelle : Chiffre d’affaires mensuel", exact: true }).getByRole("row", { name: /2026-01/ }).getByRole("cell")).toHaveText(["10", "À compléter"]);
});

test("objectif : envoyer des bornes décimales depuis un taux et lire une cible entière inaccessible", async ({ page }) => {
  await mockWorkspace(page); let request: Record<string, unknown> | null = null;
  await page.route("**/api/**/questionnaire", route => route.fulfill({ json: { questions: [{ field_id: "growth", sheet: "Control", cell: "C12", label: "Croissance", value_type: "percent", value: .1 }] } }));
  await page.route("**/api/**/goals", route => {
    if (route.request().method() === "POST") { request = route.request().postDataJSON(); return route.fulfill({ json: { job: { id: "goal", status: "QUEUED" } } }); }
    return route.fulfill({ json: { goals: [{ id: "integer-goal", result: { status: "DISCRETE_TARGET_UNREACHABLE", target: "5", candidate: { lever: "2", value: "4", residual: "-1" } } }] } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Cible inaccessible avec les valeurs entières voisines" })).toBeVisible();
  await page.getByLabel("Levier à ajuster").selectOption("growth|Control|C12");
  await page.getByLabel("Valeur cible (€)").fill("10.5");
  await page.getByLabel("Borne inférieure du levier").fill("0.05");
  await page.getByLabel("Borne supérieure du levier").fill("0.20");
  // Submit while the numeric field remains focused: native HTML validation
  // must accept fractions before React's blur handler updates its defaultValue.
  await page.getByLabel("Borne supérieure du levier").press("Enter");
  await expect.poll(() => request).toMatchObject({ field_id: "growth", sheet: "Control", cell: "C12", target: 10.5, lower: .05, upper: .2, expected_revision: 0, request_id: expect.any(String) });
});

test("extraction : montrer les avertissements OCR et les valeurs issues de formules avant confirmation", async ({ page }) => {
  await mockWorkspace(page);
  const extraction = { id: "extracted-1", source_id: "source-1", status: "A_CONFIRMER", text: "Pièce fictive partiellement lisible", warnings: ["OCR_REQUIS_INDISPONIBLE", "OCR_ECHEC_PAGE_2", "FORMULES_CACHEES_NON_RECALCULEES"], facts: [{ id: "f000001", raw: "1250", normalized_value: "1250", label: "Résultat enregistré", cached_formula: "=SUM(A1:A3)", freshness: "NON_VERIFIEE", location: { sheet: "Données", cell: "A4" } }] };
  await page.route("**/api/**/extractions", route => route.fulfill({ json: { extractions: [extraction] } }));
  await page.route("**/api/**/extractions/extracted-1", route => route.fulfill({ json: extraction }));
  await page.route("**/api/**/questionnaire", route => route.fulfill({ json: { questions: [] } }));
  await page.goto("/atelier"); await page.getByRole("button", { name: "Documents", exact: true }).click();
  await page.getByRole("button", { name: /Examiner les preuves/ }).click();
  const modal = page.getByRole("dialog");
  await expect(modal.getByRole("alert")).toContainText("OCR local indisponible");
  await expect(modal.getByRole("alert")).toContainText("Lecture OCR échouée pour la page 2");
  await expect(modal.getByText("Valeur issue du cache d’une formule Excel, sans recalcul vérifié. Contrôlez sa fraîcheur dans la pièce source avant de la confirmer.")).toBeVisible();
  await expect(modal.getByLabel("Valeur retenue")).toHaveValue("1250");
  await expect(modal.getByRole("button", { name: "Proposer les faits sélectionnés" })).toBeDisabled();
});

test("documents : transmettre le titre choisi et ouvrir une pièce uniquement si un fichier existe", async ({ page }) => {
  const state = await mockWorkspace(page); let upload = "";
  const extraction = { id: "written", source_id: "source-1", status: "A_CONFIRMER", text: "Réponse écrite fictive", facts: [] };
  await page.route("**/api/**/extractions", route => route.fulfill({ json: { extractions: [extraction] } }));
  await page.route("**/api/**/extractions/written", route => route.fulfill({ json: extraction }));
  await page.route("**/api/**/sources/upload", route => {
    upload = route.request().postData() || "";
    state.sources.push({ id: "piece-2", title: "Justificatif d’investissement", kind: "DOCUMENT", path: "sources/piece.pdf" });
    return route.fulfill({ json: state.sources.at(-1) });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Documents", exact: true }).click();
  await page.getByRole("button", { name: /Examiner les preuves/ }).click();
  await expect(page.getByRole("dialog").getByRole("link", { name: "Ouvrir la pièce source" })).toHaveCount(0);
  await expect(page.getByRole("dialog")).toContainText("Réponse écrite fictive");
  await page.getByRole("button", { name: "Fermer les informations", exact: true }).click();
  await page.getByRole("button", { name: "Importer un document ou une réponse", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Ajouter une source" });
  await dialog.getByRole("button", { name: "Document", exact: true }).click();
  await dialog.getByLabel("Titre", { exact: true }).fill("Justificatif d’investissement");
  await dialog.locator('input[type="file"]').setInputFiles({ name: "scan-original.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-fictif") });
  await dialog.getByRole("button", { name: "Ajouter la source", exact: true }).click();
  await expect.poll(() => upload).toContain("Justificatif d’investissement");
  expect(upload).toContain('filename="scan-original.pdf"');
  await expect(page.getByRole("heading", { name: "Justificatif d’investissement", exact: true })).toBeVisible();
  await page.route("**/api/**/extractions", route => route.fulfill({ json: { extractions: [{ ...extraction, source_id: "piece-2" }] } }));
  await page.route("**/api/**/extractions/written", route => route.fulfill({ json: { ...extraction, source_id: "piece-2" } }));
  await page.reload(); await page.getByRole("button", { name: /Examiner les preuves/ }).click();
  await expect(page.getByRole("dialog").getByRole("link", { name: "Ouvrir la pièce source" })).toHaveAttribute("href", /sources\/piece-2\/file$/);
});

test("sensibilité : refuser 21 valeurs sur un axe avant tout envoi", async ({ page }) => {
  await mockWorkspace(page); let sent: number[] | null = null;
  await page.route("**/api/**/questionnaire", route => route.fulfill({ json: { questions: [{ field_id: "price", sheet: "Control", cell: "C11", label: "Prix", value_type: "number", value: 100 }] } }));
  await page.route("**/api/**/sensitivities", route => {
    if (route.request().method() === "POST") sent = route.request().postDataJSON().axes[0].values;
    return route.fulfill({ json: { campaigns: [] } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByLabel("Hypothèse de l’axe 1").selectOption("price|Control|C11");
  const values = Array.from({ length: 21 }, (_, index) => index + 1);
  await page.getByLabel("Valeurs de l’axe 1, séparées par ;").fill(values.join(" ; "));
  await expect(page.getByRole("button", { name: "Lancer la campagne" })).toBeDisabled(); expect(sent).toBeNull();
  await page.getByLabel("Valeurs de l’axe 1, séparées par ;").fill(values.slice(0, 20).join(" ; "));
  await page.getByRole("button", { name: "Lancer la campagne" }).click();
  await expect.poll(() => sent).toEqual(values.slice(0, 20));
});

test("CSV Windows : choisir explicitement l’encodage après le diagnostic et avant l’aperçu", async ({ page }) => {
  await mockWorkspace(page); const requests: string[] = [];
  await page.route("**/api/**/actuals", route => route.fulfill({ json: { rows: [], metrics_catalog: [{ id: "cash", label: "Trésorerie", kind: "balance", unit: "EUR" }] } }));
  await page.route("**/api/**/actuals/import", route => {
    const body = route.request().postData() || "";
    const field = (name: string) => new RegExp('name="' + name + '"\\r?\\n\\r?\\n([^\\r\\n]+)').exec(body)?.[1];
    requests.push(field("encoding") || "absent");
    if (field("encoding") === "utf-8") return route.fulfill({ status: 409, json: { detail: "Le CSV ne peut pas être lu en UTF-8. Choisir son encodage dans le formulaire (UTF-8 ou Windows-1252), puis relire le fichier." } });
    expect(field("encoding")).toBe("cp1252");
    expect(route.request().postDataBuffer()?.includes(Buffer.from("période;poste;valeur", "latin1"))).toBe(true);
    const mapping = JSON.parse(field("mapping") || "{}");
    if (!Object.keys(mapping).length) return route.fulfill({ json: { columns: ["période", "poste", "valeur"], rows: [], encoding: "cp1252" } });
    expect(mapping).toMatchObject({ period: "période", metric: "poste", value: "valeur" });
    return route.fulfill({ json: { encoding: "cp1252", preview: { approval_token: "encoding-preview", changes: [{ period: "2026-01", metric: "cash", old: null, new: "10.50" }] } } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Réalisé", exact: true }).click();
  await page.getByLabel("Date d’arrêté du réalisé").fill("2026-01-31");
  await page.getByLabel("Fichier du réalisé").setInputFiles({ name: "realise.csv", mimeType: "text/csv", buffer: Buffer.from("période;poste;valeur\n2026-01;cash;10,50\n", "latin1") });
  await page.getByRole("button", { name: "Lire les colonnes du fichier" }).click();
  await expect(page.getByRole("alert")).toContainText("Choisir son encodage");
  await page.getByLabel("Encodage du CSV").selectOption("cp1252");
  await page.getByRole("button", { name: "Lire les colonnes du fichier" }).click();
  await page.getByRole("combobox", { name: "Période", exact: true }).selectOption("période");
  await page.getByRole("combobox", { name: "Poste métier", exact: true }).selectOption("poste");
  await page.getByRole("combobox", { name: "Valeur", exact: true }).selectOption("valeur");
  await page.getByRole("button", { name: "Prévisualiser les lignes importées" }).click();
  await expect(page.getByRole("dialog", { name: "Aperçu du réalisé" })).toBeVisible();
  expect(requests).toEqual(["utf-8", "cp1252", "cp1252"]);
});

test("import du réalisé : associer le libellé source au poste métier avant l’aperçu", async ({ page }) => {
  await mockWorkspace(page); let adopted = false;
  const catalog = [{ id: "revenue", label: "Chiffre d’affaires", kind: "flow", unit: "EUR" }];
  await page.route("**/api/**/actuals", route => route.fulfill({ json: { rows: [], metrics_catalog: catalog } }));
  await page.route("**/api/**/actuals/import", route => {
    const body = route.request().postData() || "";
    const field = (name: string) => JSON.parse(new RegExp('name="' + name + '"\\r?\\n\\r?\\n([^\\r\\n]+)').exec(body)?.[1] || "{}");
    const mapping = field("mapping"), metrics = field("metric_mapping");
    const columns = ["Mois", "Libellé", "Montant"];
    if (!Object.keys(mapping).length) return route.fulfill({ json: { columns, rows: [] } });
    expect(mapping).toMatchObject({ period: "Mois", metric: "Libellé", value: "Montant" });
    if (!metrics.CA) return route.fulfill({ json: { columns, metric_values: ["CA"], needs_metric_mapping: true } });
    expect(metrics.CA).toBe("revenue");
    return route.fulfill({ json: { columns, preview: { approval_token: "actual-import", changes: [{ metric: "revenue", old: null, new: "1234.5" }] } } });
  });
  await page.route("**/api/**/actuals/apply", route => { adopted = true; return route.fulfill({ json: {} }); });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Réalisé", exact: true }).click();
  await page.getByLabel("Date d’arrêté du réalisé").fill("2027-01-31");
  await page.getByLabel("Fichier du réalisé").setInputFiles({ name: "ventes.csv", mimeType: "text/csv", buffer: Buffer.from("Mois;Libellé;Montant\n2027-01;CA;1234,50") });
  await page.getByRole("button", { name: "Lire les colonnes du fichier" }).click();
  await page.getByRole("combobox", { name: "Période", exact: true }).selectOption("Mois");
  await page.getByRole("combobox", { name: "Poste métier", exact: true }).selectOption("Libellé");
  await page.getByRole("combobox", { name: "Valeur", exact: true }).selectOption("Montant");
  await page.getByRole("button", { name: "Prévisualiser les lignes importées" }).click();
  await expect(page.getByRole("button", { name: "Prévisualiser les lignes importées" })).toBeDisabled();
  await page.getByLabel("Correspondance du poste : CA", { exact: true }).selectOption("revenue");
  await page.getByRole("button", { name: "Prévisualiser les lignes importées" }).click();
  await expect(page.getByRole("dialog", { name: "Aperçu du réalisé" })).toContainText("1234.5");
  expect(adopted).toBe(false);
});

test("lot de 20 000 cellules : examiner la dernière page sans créer 20 000 lignes DOM", async ({ page }) => {
  const state = await mockWorkspace(page);
  state.draft.status = "DRAFT";
  state.draft.operations = Array.from({ length: 20000 }, (_, index) => ({ type: "set_value", sheet: "Control", cell: "A" + (index + 1), value: index + 1 }));
  await page.goto("/atelier"); await page.getByRole("button", { name: "Voir le lot", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Brouillon partagé" });
  await expect(dialog.locator("tbody tr")).toHaveCount(200);
  await page.getByLabel("Page des modifications", { exact: true }).selectOption("99");
  await expect(dialog).toContainText("Control · A20000");
  await page.getByRole("button", { name: "Vérifier l’aperçu", exact: true }).click();
  await expect(page.getByRole("table", { name: "Aperçu des modifications avant et après" })).toBeVisible();
  await expect(dialog.locator("tbody tr")).toHaveCount(200);
  await page.getByLabel("Page des modifications", { exact: true }).selectOption("99");
  await expect(dialog).toContainText("Control · A20000");
  await page.getByRole("button", { name: "Fermer", exact: true }).click();
  await expect(page.getByLabel("Message aux agents")).toBeEditable();
  expect(state.case.revision).toBe(0);
});

test("intention ambiguë : lire l’état puis clôturer explicitement sans réexécution", async ({ page }) => {
  await mockWorkspace(page); let executed = 0, reviewed = false, requestId = "";
  await page.route("**/api/**/recalculate", route => { executed++; requestId = route.request().postDataJSON().request_id; return route.fulfill({ status: 409, json: { detail: "La demande précédente nécessite un examen.", review_required: true } }); });
  await page.route("**/api/**/intents/*/review", route => {
    if (route.request().method() === "GET") return route.fulfill({ json: { approval_token: "review-state-token", current_revision: 0, operation: "recalculate", status: "REVIEW_REQUIRED", summary: "Le dossier reste en révision 0. Aucun travail en cours." } });
    expect(route.request().postDataJSON()).toEqual({ approval_token: "review-state-token", expected_revision: 0 }); reviewed = true; return route.fulfill({ json: { status: "REVIEWED" } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Recalculer", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "Examiner une demande interrompue" })).toContainText("Le dossier reste en révision 0.");
  expect(reviewed).toBe(false);
  expect(await page.evaluate(id => Object.entries(localStorage).some(([key, value]) => key.startsWith("tca.intent.v1.") && value === id), requestId)).toBe(true);
  await page.getByRole("button", { name: "Clôturer cette demande sans la rejouer" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0); expect(reviewed).toBe(true); expect(executed).toBe(1);
  expect(await page.evaluate(id => Object.entries(localStorage).some(([key, value]) => key.startsWith("tca.intent.v1.") && value === id), requestId)).toBe(false);
});

test("copie démesurée : refuser avant toute lecture supplémentaire", async ({ page }) => {
  const state = await mockWorkspace(page);
  await page.goto("/atelier"); await expect(page.getByLabel("Valeur ou formule de la cellule")).toHaveValue("Hypothèses de travail");
  await page.getByTestId("data-grid-canvas").focus();
  await page.keyboard.press("Control+a");
  const reads = state.requests.filter(request => request.path.endsWith("/cells")).length;
  await page.keyboard.press("Control+c");
  await expect(page.getByRole("alert")).toContainText("Limitez la copie à 20 000 cellules");
  expect(state.requests.filter(request => request.path.endsWith("/cells")).length).toBe(reads);
});

test("navigation prolongée : relire un bloc évincé puis copier la valeur courante", async ({ page, context }) => {
  await mockWorkspace(page); await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  const loadedRows: number[] = [];
  await page.route("**/api/**/sheets", route => route.fulfill({ json: { sheets: [{ name: "Control", rows: 5000, columns: 40 }] } }));
  await page.route("**/api/**/cells?*", route => {
    const query = new URL(route.request().url()).searchParams, row = Number(query.get("row"));
    loadedRows.push(row);
    return route.fulfill({ json: { cells: row === 1 ? [{ cell: "A1", row: 1, column: 1, value: "Valeur courante copiée" }] : [] } });
  });
  await page.goto("/atelier"); await expect(page.getByLabel("Valeur ou formule de la cellule")).toHaveValue("Valeur courante copiée");
  const initialReads = loadedRows.filter(row => row === 1).length;
  for (const row of [501, 1001, 1501, 2001, 2501]) {
    await page.getByLabel("Adresse de cellule").fill("A" + row); await page.getByLabel("Adresse de cellule").press("Enter");
    await expect.poll(() => loadedRows.some(loaded => loaded >= row - 100)).toBe(true);
  }
  await page.getByLabel("Adresse de cellule").fill("A1"); await page.getByLabel("Adresse de cellule").press("Enter");
  await expect.poll(() => loadedRows.filter(row => row === 1).length).toBeGreaterThan(initialReads);
  await expect(page.getByLabel("Valeur ou formule de la cellule")).toHaveValue("Valeur courante copiée");
  await page.getByTestId("data-grid-canvas").focus(); await page.keyboard.press("Control+c");
  await expect.poll(() => page.evaluate(() => navigator.clipboard.readText())).toContain("Valeur courante copiée");
});

test("qualification fiscale : source et validité examinées avant adoption", async ({ page }) => {
  await mockWorkspace(page); let applied = false;
  await page.route("**/api/**/qualifications", route => route.fulfill({ json: { modules: [{ id: "REGLES_FISCALES", label: "Règles fiscales" }], declarations: [], questions: [] } }));
  await page.route("**/api/**/qualifications/preview", route => { expect(route.request().postDataJSON().declaration).toMatchObject({ module: "REGLES_FISCALES", state: "ACTIF", status: "HYPOTHESE", evidence: "source-1", jurisdiction: "France", valid_from: "2027-01-01", valid_to: "2027-12-31" }); return route.fulfill({ json: { approval_token: "qualified-token" } }); });
  await page.route("**/api/**/qualifications/apply", route => { expect(route.request().postDataJSON().approval_token).toBe("qualified-token"); applied = true; return route.fulfill({ json: {} }); });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Hypothèses guidées" }).click();
  await page.getByLabel("Module à qualifier").selectOption("REGLES_FISCALES");
  await expect(page.getByLabel("Application du module")).toHaveValue("ACTIF");
  await page.getByLabel("Qualification de la déclaration").selectOption("HYPOTHESE");
  await page.getByLabel("Source de la qualification").selectOption("source-1");
  await page.getByLabel("Juridiction fiscale").fill("France");
  await page.getByLabel("Début de validité fiscale").fill("2027-01-01");
  await page.getByLabel("Fin de validité fiscale").fill("2027-12-31");
  await page.getByLabel("Justification de la qualification").fill("Hypothèse fictive à vérifier.");
  await page.getByRole("button", { name: "Examiner cette qualification" }).click();
  await expect(page.getByRole("dialog", { name: "Aperçu de la qualification" })).toContainText("Hypothèses de recette");
  expect(applied).toBe(false);
  await page.getByRole("button", { name: "Approuver et adopter" }).click(); await expect.poll(() => applied).toBe(true);
});

test("requêtes simultanées : la fin du dossier A ne déverrouille pas le dossier B", async ({ page }) => {
  const state = await mockWorkspace(page), other = { ...state.case, id: "other-ui", name: "Autre entreprise" };
  let releaseA: (() => void) | undefined, releaseB: (() => void) | undefined;
  await page.route("**/api/cases", route => route.fulfill({ json: { cases: [state.case, other] } }));
  await page.route("**/api/cases/other-ui", route => route.fulfill({ json: other }));
  await page.route("**/api/**/recalculate", async route => { await new Promise<void>(resolve => { if (route.request().url().includes("other-ui")) releaseB = resolve; else releaseA = resolve; }); return route.fulfill({ json: { job: { id: "done", status: "SUCCEEDED", kind: "recalculate" } } }); });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Recalculer", exact: true }).click();
  await expect.poll(() => !!releaseA).toBe(true);
  await page.getByRole("button", { name: "Autre entreprise", exact: false }).click();
  await expect(page.getByRole("button", { name: "Recalculer", exact: true })).toBeEnabled();
  await page.getByRole("button", { name: "Recalculer", exact: true }).click(); await expect.poll(() => !!releaseB).toBe(true);
  releaseA!();
  await expect(page.getByRole("button", { name: "Recalculer", exact: true })).toBeDisabled();
  releaseB!(); await expect(page.getByRole("button", { name: "Recalculer", exact: true })).toBeEnabled();
});

test("proposition retardée : le dossier A ne peut pas ouvrir le brouillon du dossier B", async ({ page }) => {
  const state = await mockWorkspace(page), other = { ...state.case, id: "other-ui", name: "Autre entreprise" };
  let release: (() => void) | undefined;
  const submitted: Record<string, unknown>[] = [];
  await page.route("**/api/cases", route => route.fulfill({ json: { cases: [state.case, other] } }));
  await page.route("**/api/cases/other-ui", route => route.fulfill({ json: other }));
  await page.route("**/api/cases/demo-ui/offers", async route => {
    submitted.push(route.request().postDataJSON());
    await new Promise<void>(resolve => { release = resolve; });
    await route.fulfill({ json: { status: "DRAFT", operations: [{ type: "extend_offer", sheet: "Control", name: "Offre de A" }] } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Scénarios", exact: true }).click();
  await page.getByLabel("Nom de la nouvelle offre", { exact: true }).fill("Offre de A");
  await page.getByRole("button", { name: "Préparer une offre supplémentaire", exact: true }).click();
  await expect.poll(() => typeof release).toBe("function");
  await page.getByRole("button", { name: "Autre entreprise", exact: false }).click();
  await expect(page.getByRole("heading", { name: "Autre entreprise", exact: true })).toBeVisible();
  const completed = page.waitForResponse(response => response.url().endsWith("/cases/demo-ui/offers"));
  release!(); await completed; await page.waitForLoadState("networkidle");
  await expect(page.getByRole("dialog", { name: "Brouillon partagé" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Autre entreprise", exact: true })).toBeVisible();
  expect(submitted).toHaveLength(1);
  expect(submitted[0]).toMatchObject({ name: "Offre de A", expected_revision: 0, request_id: expect.any(String) });
  expect(state.requests.some(r => r.path.endsWith("/draft/apply"))).toBe(false);
});

test("raccord : saisie sourcée, aucune politique implicite et correction équilibrée", async ({ page }) => {
  await mockWorkspace(page); let submitted: Record<string, any> | null = null;
  await page.route("**/api/**/actuals", route => route.fulfill({ json: { rows: [{ period: "2027-01", metric: "revenue", kind: "flow", value: 100, unit: "EUR" }], forecast_status: "A_COMPLETER_OU_RECALCULER", annual_balance: [{ period: "2027", assets: null, liabilities: null, equity: null, net_income: null, balance_check: null, model_balance_check: null }] } }));
  await page.route("**/api/**/actuals/bridge/questions", route => route.fulfill({ json: { workbook_sha256: "fictive-current-sha", cutoff: "2027-01-31", baseline_fields: [{ id: "assets", value: 1000, linked: true }], periods: ["2027-02"], questions: ["Les autres postes restent à qualifier."], bridge: submitted?.bridge } }));
  await page.route("**/api/**/actuals/reforecast", route => { submitted = route.request().postDataJSON(); return route.fulfill({ json: { operations: [], status: "NEEDS_INPUT" } }); });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Réalisé", exact: true }).click();
  await page.getByText("Bilan et résultat annuels actualisés", { exact: true }).click();
  await expect(page.getByRole("table", { name: "Bilan et résultat annuels actualisés" }).getByRole("cell", { name: "À compléter", exact: true })).toHaveCount(6);
  await page.getByText("Préparer le raccord du réalisé dans Excel", { exact: true }).click();
  await expect(page.getByLabel("Total actif du modèle à l’arrêté", { exact: true })).toHaveAttribute("readonly", "");
  await page.getByText("Trésorerie · À définir", { exact: true }).click();
  await expect(page.getByLabel("Traitement : Trésorerie", { exact: true })).toHaveValue("");
  await page.getByLabel("Traitement : Trésorerie", { exact: true }).selectOption("carry");
  await page.getByLabel("Fin d’horizon : Trésorerie", { exact: true }).selectOption("carry_remaining");
  await page.getByLabel("Source du traitement : Trésorerie", { exact: true }).selectOption("source-1");
  await page.getByLabel("Justification : Trésorerie", { exact: true }).fill("Écart fictif conservé.");
  await page.getByRole("button", { name: "Ajouter une correction mensuelle" }).click();
  await page.getByLabel("Mois de correction 1", { exact: true }).fill("2027-02");
  await page.getByLabel("Nature de correction 1", { exact: true }).selectOption("balance_transfer");
  await page.getByLabel("Source de correction 1", { exact: true }).selectOption("source-1");
  await page.getByLabel("Explication de correction 1", { exact: true }).fill("Encaissement net non prévu dans le modèle.");
  await page.getByLabel("Compte correction 1, écriture 1", { exact: true }).selectOption("cash");
  await page.getByLabel("Débit correction 1, écriture 1", { exact: true }).fill("100,50");
  await page.getByLabel("Flux de trésorerie correction 1, écriture 1", { exact: true }).selectOption("receipts");
  await page.getByLabel("Compte correction 1, écriture 2", { exact: true }).selectOption("receivables");
  await page.getByLabel("Crédit correction 1, écriture 2", { exact: true }).fill("100,50");
  await page.getByRole("button", { name: "Préparer le raccord dans Excel", exact: true }).click();
  await expect.poll(() => submitted).not.toBeNull();
  expect(submitted!.bridge).toMatchObject({ schema: "tca-reforecast-bridge/1", basis: "NET_ADJUSTMENTS_TO_CURRENT_MODEL", workbook_sha256: "fictive-current-sha", policies: { cash: { treatment: "carry", terminal: "carry_remaining", evidence_id: "source-1" } }, events: [{ kind: "balance_transfer", entries: [{ account: "cash", debit: 100.5, credit: 0, cash_flow: "receipts" }, { account: "receivables", debit: 0, credit: 100.5 }] }] });
  expect(submitted!.bridge.policies.inventory).toBeUndefined();
  await expect(page.getByText("Les autres postes restent à qualifier.", { exact: true })).toBeVisible();
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("aperçu de structure : indiquer l’échantillon et rendre le manifeste complet accessible", async ({ page }) => {
  const state = await mockWorkspace(page); state.draft.status = "READY"; state.draft.approval_token = "reviewed";
  state.draft.operations = [{ type: "extend_offer", sheet: "CA", name: "Offre 14" }];
  state.draft.validation = { preview_details: { filename: "apercu.variant.json", sha256: "a".repeat(64), size: 1500000, total_changes: 20732 } };
  await page.goto("/atelier"); await page.getByRole("button", { name: "Voir le lot", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("échantillon");
  await expect(page.getByRole("dialog")).toContainText("20 732 changements");
  await expect(page.getByRole("link", { name: "Télécharger tous les changements de structure" })).toHaveAttribute("href", "/api/cases/demo-ui/draft/preview-details");
  expect(state.case.revision).toBe(0);
});

test("téléchargement refusé : conserver l’atelier et le message en cours", async ({ page }) => {
  await mockWorkspace(page);
  await page.route("**/api/**/download", route => route.fulfill({ status: 409, json: { detail: "Le classeur est temporairement indisponible." } }));
  await page.goto("/atelier");
  const composer = page.getByRole("textbox", { name: "Message aux agents" });
  await composer.fill("Mon hypothèse en cours de rédaction");
  await page.getByRole("button", { name: "Classeur", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("temporairement indisponible");
  await expect(composer).toHaveValue("Mon hypothèse en cours de rédaction");
  await expect(page.getByRole("heading", { name: "Développement · recette interface" })).toBeVisible();
  expect(new URL(page.url()).pathname).toBe("/atelier");
});
