import { test, expect } from "@playwright/test";
import fs from "node:fs/promises";
import { randomUUID } from "node:crypto";

test("profil sur API réelle : champs canoniques, changement de dossier, sauvegarde et reprise", async ({ page }, testInfo) => {
  const errors: string[] = [], mutations: { method: string; path: string }[] = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("request", request => { if (request.url().includes("/api/") && request.method() !== "GET") mutations.push({ method: request.method(), path: new URL(request.url()).pathname }); });
  const cases: { id: string; name: string; revision: number; sha256: string }[] = [];
  for (const suffix of ["A", "B"]) {
    const created = await page.request.post("/api/cases", { data: { client_name: "Organisation fictive profil", name: `Recette profil ${suffix} ${randomUUID()}` } });
    expect(created.status()).toBe(200);
    const body = await created.json(), value = body.case || body;
    const current = await (await page.request.get(`/api/cases/${value.id}`)).json();
    cases.push(current);
  }
  const [a, b] = cases;
  const originalA = { name: "Entreprise fictive A", activity: "services", start_year: 2026, years: 2, activity_start_month: 4, business_model: "services", horizon_years: 5, revenue_model: "alias périmé", activity_start: "2026-01-01", extension: { import_id: "fictif", preserved: [1, 7] }, objectives: "Avant édition" };
  const originalB = { name: "Entreprise fictive B", activity: "trading", start_year: 2028, years: 7, activity_start_month: 9, business_model: "négoce", extension: { dossier: "B" } };
  for (const [record, profile] of [[a, originalA], [b, originalB]] as const) {
    const response = await page.request.put(`/api/cases/${record.id}/profile`, { data: { expected_revision: record.revision, request_id: randomUUID(), profile } });
    expect(response.status()).toBe(200);
  }
  await page.addInitScript(id => localStorage.setItem("tca.case", id), a.id);
  await page.goto("/atelier"); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("2");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveValue("2026-04-01");
  await expect(page.getByLabel("Modèle de revenus")).toHaveValue("services");
  await page.getByLabel("Décisions à préparer").fill("Modification du seul objectif A");
  await page.getByRole("button", { name: "Enregistrer le profil", exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: "Demande enregistrée" })).toBeVisible();
  const savedA = await (await page.request.get(`/api/cases/${a.id}/profile`)).json();
  expect(savedA.profile).toMatchObject({ years: 2, horizon_years: 2, activity_start_month: 4, activity_start: "2026-04-01", business_model: "services", revenue_model: "services", extension: originalA.extension, objectives: "Modification du seul objectif A" });
  await page.reload(); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("2");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveValue("2026-04-01");
  await expect(page.getByLabel("Décisions à préparer")).toHaveValue("Modification du seul objectif A");
  await page.getByLabel("Nom de l’entreprise").fill("Saisie locale A non enregistrée");
  await page.getByRole("button", { name: b.name, exact: false }).click();
  await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect(page.getByLabel("Nom de l’entreprise")).toHaveValue(originalB.name);
  await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("7");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveValue("2028-09-01");
  await page.getByLabel("Décisions à préparer").fill("Objectif B conservé");
  await page.getByRole("button", { name: "Enregistrer le profil", exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: "Demande enregistrée" })).toBeVisible();
  const savedB = await (await page.request.get(`/api/cases/${b.id}/profile`)).json();
  expect(savedB.profile).toMatchObject({ ...originalB, objectives: "Objectif B conservé" });
  expect((await (await page.request.get(`/api/cases/${a.id}/profile`)).json()).profile).toEqual(savedA.profile);
  for (const record of cases) {
    const current = await (await page.request.get(`/api/cases/${record.id}`)).json();
    expect(current.revision).toBe(record.revision); expect(current.sha256).toBe(record.sha256);
    expect((await (await page.request.get(`/api/cases/${record.id}/jobs`)).json()).jobs).toHaveLength(0);
    const draft = await (await page.request.get(`/api/cases/${record.id}/draft`)).json();
    expect(draft.operations || []).toHaveLength(0);
  }
  expect(errors).toEqual([]);
  expect(mutations).toHaveLength(2);
  expect(mutations.every(item => item.method === "PUT" && item.path.endsWith("/profile"))).toBe(true);
  await page.screenshot({ path: testInfo.outputPath("profil-B-verifie.png"), fullPage: true });
  await fs.writeFile(testInfo.outputPath("receipt.json"), JSON.stringify({ status: "PASS_REAL_API_PROFILE_ROUNDTRIP", cases, savedA: savedA.profile, savedB: savedB.profile, canonical_fields_loaded: true, conflicting_aliases_corrected: true, unknown_extensions_preserved: true, reloaded_profile_preserved: true, case_switch_isolated: true, workbook_hashes_and_revisions_unchanged: true, financial_drafts_empty: true, jobs_created: 0, browser_errors: errors, browser_mutations: mutations, limits: ["Two fictitious cases and company profiles only; no financial proposal, Excel calculation or provider call."] }, null, 2));
});
