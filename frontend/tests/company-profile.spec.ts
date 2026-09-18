import { expect, test } from "@playwright/test";
import { companyProfileForForm, editCompanyProfile } from "../src/companyProfile";
import type { CompanyProfile } from "../src/workshopTypes";
import { mockWorkspace } from "./fixture";

test("profil : les champs API priment sur des alias historiques contradictoires", () => {
  const original: CompanyProfile = { years: 2, horizon_years: 5, start_year: 2026, activity_start_month: 4, activity_start: "2026-01-12", business_model: "abonnement", revenue_model: "autre", extension: { source: "historique", values: [1, 2] } };
  const before = structuredClone(original), form = companyProfileForForm(original);
  expect(form).toMatchObject({ years: 2, horizon_years: 2, business_model: "abonnement", revenue_model: "abonnement", activity_start_month: 4, activity_start: "2026-04-01", extension: original.extension });
  const saved = companyProfileForForm(editCompanyProfile(form, "objectives", "Nouvel objectif"));
  expect(saved).toEqual({ ...form, objectives: "Nouvel objectif" });
  expect(original).toEqual(before);
});

test("profil historique : reprendre les alias puis conserver le mois lors d’un changement d’année", () => {
  const form = companyProfileForForm({ start_year: 2026, horizon_years: 3, revenue_model: "contrats", activity_start: "2026-07-19", custom: "conservé" });
  expect(form).toMatchObject({ years: 3, business_model: "contrats", activity_start_month: 7, activity_start: "2026-07-19" });
  const saved = companyProfileForForm(editCompanyProfile(editCompanyProfile(editCompanyProfile(form, "start_year", 2028), "horizon_years", 8), "revenue_model", "abonnements et projets"));
  expect(saved).toMatchObject({ start_year: 2028, years: 8, horizon_years: 8, business_model: "abonnements et projets", revenue_model: "abonnements et projets", activity_start_month: 7, activity_start: "2028-07-01", custom: "conservé" });
});

test("profil API : charger, modifier un autre champ, enregistrer et recharger sans changer le calendrier", async ({ page }) => {
  await mockWorkspace(page);
  let profile: CompanyProfile = { name: "Profil API", start_year: 2026, years: 2, activity_start_month: 4, business_model: "abonnement", horizon_years: 5, revenue_model: "périmé", activity_start: "2026-01-01", extension: { opaque: ["conservé", 17] } };
  const writes: CompanyProfile[] = [];
  await page.route("**/api/**/profile", route => {
    if (route.request().method() === "PUT") { profile = route.request().postDataJSON().profile; writes.push(profile); }
    return route.fulfill({ json: { profile } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("2");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveValue("2026-04-01");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveAttribute("min", "2026-01-01");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveAttribute("max", "2026-12-31");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveAttribute("required", "");
  await expect(page.getByLabel("Modèle de revenus")).toHaveValue("abonnement");
  await page.getByLabel("Décisions à préparer").fill("Comparer un recrutement");
  await page.getByRole("button", { name: "Enregistrer le profil", exact: true }).click();
  await expect.poll(() => writes.length).toBe(1);
  expect(profile).toMatchObject({ years: 2, horizon_years: 2, business_model: "abonnement", revenue_model: "abonnement", activity_start_month: 4, activity_start: "2026-04-01", extension: { opaque: ["conservé", 17] }, objectives: "Comparer un recrutement" });
  await page.reload(); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("2");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveValue("2026-04-01");
  await expect(page.getByLabel("Décisions à préparer")).toHaveValue("Comparer un recrutement");
});

test("changement de dossier : attendre le profil B et ne pas lui enregistrer la saisie A", async ({ page }) => {
  const state = await mockWorkspace(page), other = { ...state.case, id: "profile-b", name: "Entreprise B" };
  const profiles: Record<string, CompanyProfile> = {
    "demo-ui": { name: "Entreprise A", start_year: 2026, years: 2, activity_start_month: 4, business_model: "contrats A" },
    "profile-b": { name: "Entreprise B", start_year: 2028, years: 7, activity_start_month: 9, business_model: "contrats B", extension: "B" },
  };
  const writes: { id: string; profile: CompanyProfile }[] = [];
  let releaseB!: () => void, requestedB = false;
  const delayedB = new Promise<void>(resolve => { releaseB = resolve; });
  await page.route("**/api/cases", route => route.fulfill({ json: { cases: [state.case, other] } }));
  await page.route("**/api/cases/profile-b", route => route.fulfill({ json: other }));
  await page.route("**/api/**/profile", async route => {
    const id = new URL(route.request().url()).pathname.split("/")[3];
    if (route.request().method() === "PUT") { profiles[id] = route.request().postDataJSON().profile; writes.push({ id, profile: profiles[id] }); }
    if (id === "profile-b") { requestedB = true; await delayedB; }
    return route.fulfill({ json: { profile: profiles[id] } });
  });
  await page.goto("/atelier"); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("2");
  await page.getByLabel("Nom de l’entreprise").fill("Saisie A non enregistrée");
  await page.getByRole("button", { name: "Entreprise B", exact: false }).click();
  await page.getByRole("button", { name: "Entreprise", exact: true }).click();
  await expect.poll(() => requestedB).toBe(true);
  await expect(page.getByText("Chargement du profil enregistré…", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Enregistrer le profil", exact: true })).toHaveCount(0);
  releaseB();
  await expect(page.getByLabel("Nom de l’entreprise")).toHaveValue("Entreprise B");
  await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("7");
  await expect(page.getByLabel("Démarrage de l’activité")).toHaveValue("2028-09-01");
  await page.getByLabel("Décisions à préparer").fill("Objectif B");
  await page.getByRole("button", { name: "Enregistrer le profil", exact: true }).click();
  await expect.poll(() => writes.length).toBe(1);
  expect(writes[0]).toMatchObject({ id: "profile-b", profile: { name: "Entreprise B", years: 7, activity_start_month: 9, business_model: "contrats B", extension: "B", objectives: "Objectif B" } });
  expect(profiles["demo-ui"].name).toBe("Entreprise A");
});

test("profil : une réponse lente conserve les saisies faites pendant la sauvegarde", async ({ page }) => {
  await mockWorkspace(page);
  let stored: CompanyProfile = { name: "Profil lent", start_year: 2026, years: 2, activity_start_month: 4, business_model: "services", extension: "conservée" };
  const writes: CompanyProfile[] = [];
  let release!: () => void;
  const pending = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/**/profile", async route => {
    if (route.request().method() === "PUT") {
      const submitted = route.request().postDataJSON().profile as CompanyProfile;
      writes.push(submitted);
      if (writes.length === 1) await pending;
      stored = submitted;
    }
    return route.fulfill({ json: { profile: stored } });
  });
  try {
    await page.goto("/atelier"); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
    await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("2");
    await page.getByLabel("Décisions à préparer").fill("Premier objectif envoyé");
    const save = page.getByRole("button", { name: "Enregistrer le profil", exact: true });
    const propose = page.getByRole("button", { name: "Proposer ce calendrier au classeur", exact: true });
    await save.click();
    await expect.poll(() => writes.length).toBe(1);
    await expect(save).toBeDisabled();
    await page.getByLabel("Décisions à préparer").fill("Nouvel objectif encore local");
    await page.getByLabel("Horizon du prévisionnel").selectOption("3");
    release();
    await expect(save).toBeEnabled();
    await expect(page.getByLabel("Décisions à préparer")).toHaveValue("Nouvel objectif encore local");
    await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("3");
    await expect(propose).toBeDisabled();
    expect(stored).toMatchObject({ objectives: "Premier objectif envoyé", years: 2 });
    await save.click();
    await expect.poll(() => writes.length).toBe(2);
    await expect(propose).toBeEnabled();
    expect(stored).toMatchObject({ objectives: "Nouvel objectif encore local", years: 3, activity_start_month: 4, extension: "conservée" });
    await page.reload(); await page.getByRole("button", { name: "Entreprise", exact: true }).click();
    await expect(page.getByLabel("Décisions à préparer")).toHaveValue("Nouvel objectif encore local");
    await expect(page.getByLabel("Horizon du prévisionnel")).toHaveValue("3");
  } finally { release(); }
});
