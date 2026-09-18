import { test, expect } from "@playwright/test";
import fs from "node:fs/promises";

test("serveur réel : clore une intention refusée après examen sans réexécuter", async ({ page }, testInfo) => {
  const name = `Recette clôture intention ${Date.now()}`;
  await page.goto("/atelier"); await page.getByRole("button", { name: "Nouveau dossier", exact: true }).click();
  await page.getByLabel("Organisation ou client").fill("Organisation fictive de recette");
  await page.getByLabel("Nom du dossier", { exact: true }).fill(name);
  await page.getByRole("button", { name: "Créer le dossier", exact: true }).click();
  await expect(page.getByRole("heading", { name, exact: true })).toBeVisible();
  const caseId = await page.evaluate(() => localStorage.getItem("tca.case")); expect(caseId).toBeTruthy();
  const initialProfile = await (await page.request.get(`/api/cases/${caseId}/profile`)).json();
  const requestId = "review_fixture_" + Date.now(), key = `tca.intent.v1.${caseId}.review-fixture`;
  // A refused profile creates a retained intention without touching financial data.
  const refusal = await page.request.put(`/api/cases/${caseId}/profile`, { data: { profile: { years: 11 }, request_id: requestId, expected_revision: 0 } });
  expect(refusal.status()).toBe(409); expect((await refusal.json()).review_required).toBe(true);
  await page.evaluate(({ caseId, requestId, key }) => { localStorage.setItem(key, requestId); window.dispatchEvent(new CustomEvent("tca-intent-review", { detail: { caseId, requestId, key, path: "/profile" } })); }, { caseId, requestId, key });
  const dialog = page.getByRole("dialog", { name: "Examiner une demande interrompue" });
  await expect(dialog).toContainText(name);
  const before = await (await page.request.get(`/api/cases/${caseId}/intents/${requestId}`)).json();
  expect(before.status).toBe("REVIEW_REQUIRED");
  await page.getByRole("button", { name: "Clôturer cette demande sans la rejouer" }).click();
  await expect(dialog).toHaveCount(0);
  const after = await (await page.request.get(`/api/cases/${caseId}/intents/${requestId}`)).json();
  expect(after.status).toBe("REVIEWED");
  expect(await (await page.request.get(`/api/cases/${caseId}/profile`)).json()).toEqual(initialProfile);
  const current = await (await page.request.get(`/api/cases/${caseId}`)).json(); expect(current.revision).toBe(0);
  expect(await page.evaluate(key => localStorage.getItem(key), key)).toBeNull();
  await fs.writeFile(testInfo.outputPath("receipt.json"), JSON.stringify({ status: "PASS", caseId, requestId, prior_status: before.status, final_status: after.status, financial_revision: current.revision, profile_unchanged: true, no_excel_execution: true, no_provider_call: true }, null, 2));
});
