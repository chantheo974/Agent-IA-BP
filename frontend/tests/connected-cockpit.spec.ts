import { expect, test, type Page } from '@playwright/test';
import type { FinancialSeries } from '../src/workshopTypes';

// This fixture exercises the public cockpit contract, never its demo provider.
async function connectedFixture(page: Page) {
  const dossier = { id: 'connected-case', name: 'Dossier connecté fictif', client_name: 'Entreprise de recette', revision: 0, calculation_status: 'A_RECALCULER' };
  const source = { id: 'proof-current', title: 'Décision documentée', kind: 'Texte' };
  const sheet = { id: 'stable-calendar', name: 'Control renommé', original_name: 'Control', label: 'Calendrier du projet', purpose: 'Régler le calendrier du dossier.', role: 'Calendrier', group_id: 'framework', theme_ids: ['synthesis'], view_kind: 'settings', field_count: 1, binding_count: 1, dependencies: [], dependency_basis: 'CONTRAT_METIER_VERSIONNE', fields: [{ field_id: 'year', label: 'Année de départ', value_type: 'integer', can_propose: true, binding_count: 1 }], register: null };
  const requests: { path: string; method: string; body: Record<string, any> | null }[] = [];
  let draft: Record<string, any> = { id: 'draft-current', revision: 0, status: 'EMPTY', operations: [], changes: [], conflicts: [] };
  let value = 2026;
  const simulation = { id: 'simulation-current', name: 'Calendrier 2028', case_id: dossier.id, status: 'READY', stage: 'COMPLETE', base_revision: 0, scenario_case_id: 'simulation-copy', saved: false, stale: false, metrics: [{ id: 'revenue', label: 'Chiffre d’affaires — 2028', period: '2028', value: null, unit: 'EUR', status: 'A_COMPLETER' }], series: [] as FinancialSeries[] };
  await page.route('**/api/**', async route => {
    const request = route.request(), path = new URL(request.url()).pathname.slice(4), method = request.method();
    const body = request.postData() && request.headers()['content-type']?.includes('application/json') ? request.postDataJSON() : null;
    requests.push({ path, method, body });
    let data: unknown;
    if (path.endsWith('/events')) return route.fulfill({ contentType: 'text/event-stream', body: ': mock\n\n' });
    if (path === '/cases') data = { cases: [dossier] };
    else if (path === '/cases/' + dossier.id) data = dossier;
    else if (path.endsWith('/profile')) data = { profile: { name: 'Entreprise de recette', years: 3, start_year: 2026 } };
    else if (path.endsWith('/sheets') && !path.includes('/cockpit/')) data = { sheets: [{ name: sheet.name, rows: 200, columns: 26 }] };
    else if (path.endsWith('/sources')) data = { sources: [source] };
    else if (path.endsWith('/agents')) data = { agents: [{ id: 'agent-1', sheet: sheet.name, role: 'Calendrier du dossier' }] };
    else if (path.endsWith('/jobs')) data = { jobs: [] };
    else if (path.endsWith('/chat')) data = { messages: [] };
    else if (path.endsWith('/versions')) data = { versions: [{ id: 'version-0', revision: 0, kind: 'CREATE', current: true }] };
    else if (path.endsWith('/cockpit/catalog')) data = { schema: 'tca-cockpit/1', case_id: dossier.id, revision: dossier.revision, calculation_status: dossier.calculation_status, profile_version: '1', profile_sha256: 'profile-fixture', groups: [{ id: 'framework', label: 'Cadre du projet' }], themes: [{ id: 'synthesis', label: 'Synthèse et valeur' }], sheets: [sheet] };
    else if (path.endsWith('/cockpit/sheets/' + sheet.id)) data = { case_id: dossier.id, revision: dossier.revision, calculation_status: dossier.calculation_status, sheet, entries: [{ binding_id: 'stable-binding-year', field_id: 'year', sheet_id: sheet.id, sheet: sheet.name, cell: 'C10', label: 'Année de départ', value: draft.operations[0]?.value ?? value, current_value: value, proposed: !!draft.operations.length, formula: null, unit: 'année', value_type: 'integer', choices: [], status: 'HYPOTHESE', calculated: false, editable: true }], total: 1, offset: 0, limit: 100, draft: { id: draft.id, status: draft.status, current: true } };
    else if (path.endsWith('/cockpit/answers')) { draft.status = 'DRAFT'; draft.operations = body.answers.map((answer: { value: unknown; evidence_id: string }) => ({ type: 'set_value', sheet: sheet.name, cell: 'C10', value: answer.value, evidence_id: answer.evidence_id })); data = draft; }
    else if (path.endsWith('/draft/preview')) { draft.status = 'READY'; draft.approval_token = 'token-reviewed-cockpit'; draft.changes = draft.operations.map((op: Record<string, unknown>) => ({ ...op, before: { value }, after: { value: op.value } })); data = { job: { id: 'preview', kind: 'preview', status: 'SUCCEEDED' } }; }
    else if (path.endsWith('/draft/apply')) { value = draft.operations[0].value; dossier.revision++; draft = { status: 'APPLIED', operations: [], changes: [], conflicts: [] }; data = { job: { id: 'apply', kind: 'apply', status: 'SUCCEEDED' } }; }
    else if (path.endsWith('/draft')) data = draft;
    else if (path.endsWith('/scenarios/compare')) data = { scenarios: [{ id: dossier.id, case_id: dossier.id, name: 'Référence', metrics: [{ id: 'revenue', label: 'Chiffre d’affaires — 2026', period: '2026', value: null, unit: 'EUR', status: 'A_COMPLETER' }, { id: 'cash_min', label: 'Point bas mensuel', value: null, unit: 'EUR', status: 'A_COMPLETER' }], series: [{ id: 'cash', label: 'Trésorerie mensuelle', unit: 'EUR', categories: ['2026-01', '2026-02'], values: [null, null], status: 'INDISPONIBLE' }] }] };
    else if (path.endsWith('/cockpit/simulations/' + simulation.id + '/keep')) { simulation.saved = true; data = simulation; }
    else if (path.endsWith('/cockpit/simulations/' + simulation.id + '/propose-adoption')) { draft.status = 'DRAFT'; draft.id = 'draft-current'; draft.operations = [{ type: 'set_value', sheet: sheet.name, cell: 'C10', value: 2028, evidence_id: source.id }]; data = draft; }
    else if (path.endsWith('/cockpit/simulations/' + simulation.id)) data = simulation;
    else if (path.endsWith('/cockpit/simulations')) data = { simulations: [simulation] };
    else if (path.endsWith('/cockpit/draft/impacts')) data = { case_id: dossier.id, revision: dossier.revision, draft_id: draft.id, draft_fingerprint: 'captured-hypotheses', status: draft.status, changes: [], operations: draft.operations, sources: [source], affected_sheets: [sheet], conflicts: [], can_simulate: !!draft.operations.length, blocking_reasons: draft.operations.length ? [] : ['Préparez un brouillon.'] };
    else return route.fulfill({ status: 404, json: { message: 'Route absente de la fixture : ' + path } });
    return route.fulfill({ json: data });
  });
  return { dossier, requests, simulation };
}

test('cockpit réel : identités stables, source, brouillon et approbation explicite', async ({ page }, testInfo) => {
  const state = await connectedFixture(page), errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  await page.goto('/expert');
  await page.getByRole('button', { name: /Calendrier du projet/ }).click();
  await expect(page).toHaveURL(/\/expert\/feuilles\/stable-calendar/);
  await expect(page.getByLabel('Année de départ · C10', { exact: true })).toHaveValue('2026');
  await page.getByLabel('Année de départ · C10', { exact: true }).fill('2028');
  await page.getByLabel('Source des modifications', { exact: true }).selectOption('proof-current');
  await page.getByRole('button', { name: 'Proposer 1 modification(s) au brouillon', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Brouillon partagé' })).toBeVisible();
  expect(state.requests.find(request => request.path.endsWith('/cockpit/answers'))?.body).toMatchObject({ expected_revision: 0, request_id: expect.any(String), answers: [{ sheet_id: 'stable-calendar', binding_id: 'stable-binding-year', value: 2028, evidence_id: 'proof-current', status: 'HYPOTHESE' }] });
  expect(state.requests.some(request => request.path.endsWith('/draft/apply'))).toBe(false);
  await page.getByRole('button', { name: 'Vérifier l’aperçu' }).click();
  await page.screenshot({ path: testInfo.outputPath('cockpit-apercu.png'), fullPage: true });
  await page.getByRole('button', { name: 'Appliquer en nouvelle version' }).click();
  expect(state.requests.find(request => request.path.endsWith('/draft/apply'))?.body).toMatchObject({ draft_id: 'draft-current', approval_token: 'token-reviewed-cockpit', request_id: expect.any(String) });
  expect(errors).toEqual([]);
});

test('cockpit réel : aucune valeur fictive ou zéro implicite dans les indicateurs manquants', async ({ page }, testInfo) => {
  await connectedFixture(page); await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Vos chiffres au service de vos décisions' })).toBeVisible();
  await expect(page.getByText('Chiffre d’affaires — 2026', { exact: true })).toBeVisible();
  await expect(page.locator('article').filter({ hasText: 'Chiffre d’affaires — 2026' }).locator('p').nth(1)).toHaveText('À compléter');
  await expect(page.locator('article').filter({ hasText: 'Point bas mensuel' }).locator('p').nth(1)).toHaveText('À compléter');
  await expect(page.getByText('0 €', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Atlas Mobility', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Données de démonstration', { exact: true })).toHaveCount(0);
  await expect(page.getByText(/Les mois seront affichés après saisie/)).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('cockpit-accueil.png'), fullPage: true });
});

test('cockpit réel : le compagnon conserve la feuille renommée et libère le focus pour ajouter une source', async ({ page }, testInfo) => {
  await connectedFixture(page); await page.goto('/expert/feuilles/stable-calendar');
  await page.getByRole('button', { name: 'Discuter de cette feuille', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Votre compagnon', exact: true })).toBeVisible();
  await expect(page.getByLabel('Portée de la demande au chat')).toHaveValue('sheet');
  expect(await page.getByRole('textbox', { name: 'Message aux agents', exact: true }).evaluate(element => getComputedStyle(element).fontSize)).toBe('16px');
  await page.screenshot({ path: testInfo.outputPath('cockpit-compagnon.png'), fullPage: true });
  await page.getByRole('button', { name: 'Ajouter une source à la conversation', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Ajouter une source', exact: true })).toBeVisible();
  await expect(page.getByRole('dialog', { name: 'Votre compagnon', exact: true })).not.toBeVisible();
  await page.getByLabel('Titre', { exact: true }).fill('Preuve locale');
  await expect(page.getByLabel('Titre', { exact: true })).toHaveValue('Preuve locale');
});

test('cockpit réel : navigation mobile et liens directs sans débordement horizontal', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await connectedFixture(page); await page.goto('/expert');
  await expect(page.getByRole('heading', { name: 'Toutes les feuilles de votre modèle' })).toBeVisible();
  await page.getByRole('button', { name: 'Ouvrir la navigation', exact: true }).click();
  await page.getByRole('link', { name: 'Aujourd’hui', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Vos chiffres au service de vos décisions' })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: testInfo.outputPath('cockpit-mobile.png'), fullPage: true });
});

test('cockpit réel : conserver puis proposer une adoption ne modifie jamais la référence automatiquement', async ({ page }) => {
  const state = await connectedFixture(page); await page.goto('/simulations/simulation-current');
  await page.getByRole('button', { name: 'Conserver le scénario', exact: true }).click();
  await expect(page.getByText('Cette simulation est conservée avec ses sources et sa copie.')).toBeVisible();
  expect(state.simulation.saved).toBe(true); expect(state.dossier.revision).toBe(0);
  await page.getByRole('button', { name: 'Préparer l’adoption', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Brouillon partagé' })).toBeVisible();
  expect(state.requests.find(request => request.path.endsWith('/propose-adoption'))?.body).toMatchObject({ expected_revision: 0, request_id: expect.any(String) });
  expect(state.requests.some(request => request.path.endsWith('/draft/apply'))).toBe(false);
});

test('cockpit réel : le refus d’une révision périmée conserve les saisies pour examen', async ({ page }) => {
  const state = await connectedFixture(page); await page.goto('/expert/feuilles/stable-calendar');
  await page.getByLabel('Année de départ · C10', { exact: true }).fill('2029');
  await page.getByLabel('Source des modifications', { exact: true }).selectOption('proof-current');
  // The service owns revision rejection; a rejected proposal must retain the user's input.
  await page.route('**/api/**/cockpit/answers', route => route.fulfill({ status: 409, json: { message: 'Révision périmée : actualisez le dossier.' } }));
  await page.getByRole('button', { name: 'Proposer 1 modification(s) au brouillon', exact: true }).click();
  await expect(page.getByText('Révision périmée : actualisez le dossier.', { exact: true })).toBeVisible();
  await expect(page.getByLabel('Année de départ · C10', { exact: true })).toHaveValue('2029');
  expect(state.requests.some(request => request.path.endsWith('/draft/apply'))).toBe(false);
});

test('cockpit réel : une actualisation serveur conserve la saisie et refuse son changement de révision implicite', async ({ page }) => {
  const state = await connectedFixture(page); await page.goto('/expert/feuilles/stable-calendar');
  await page.getByLabel('Année de départ · C10', { exact: true }).fill('2029');
  await page.getByLabel('Source des modifications', { exact: true }).selectOption('proof-current');
  state.dossier.revision = 1;
  await expect(page.getByText('Révision 1', { exact: true }).first()).toBeVisible({ timeout: 20000 });
  await expect(page.getByLabel('Année de départ · C10', { exact: true })).toHaveValue('2029');
  await page.getByLabel('Année de départ · C10', { exact: true }).fill('2030');
  await page.getByRole('button', { name: 'Proposer 1 modification(s) au brouillon', exact: true }).click();
  await expect(page.getByText(/Le dossier a changé depuis vos saisies/)).toBeVisible();
  await expect(page.getByLabel('Année de départ · C10', { exact: true })).toHaveValue('2030');
  expect(state.requests.some(request => request.path.endsWith('/cockpit/answers'))).toBe(false);
});

test('cockpit réel : le chat transporte la révision et le périmètre protégé sans autoriser les formules ni la structure', async ({ page }) => {
  const state = await connectedFixture(page);
  await page.goto('/expert/feuilles/stable-calendar');
  await page.getByRole('button', { name: 'Discuter de cette feuille', exact: true }).click();
  await expect(page.getByRole('checkbox', { name: 'Autoriser les changements de structure' })).toHaveCount(0);
  await page.getByRole('textbox', { name: 'Message aux agents', exact: true }).fill('Explique les hypothèses de calendrier de ce dossier.');
  await page.getByRole('button', { name: 'Envoyer aux agents', exact: true }).click();
  await expect.poll(() => state.requests.filter(request => request.path.endsWith('/chat') && request.method === 'POST').length).toBe(1);
  expect(state.requests.find(request => request.path.endsWith('/chat') && request.method === 'POST')?.body).toMatchObject({
    request_id: expect.any(String), expected_revision: 0, mode: 'cockpit',
    selection: { sheet: 'Control renommé', allow_structure: false },
  });
  expect(state.requests.some(request => request.path.endsWith('/draft/apply'))).toBe(false);
});

test('cockpit réel : choisir un agent ouvre sa feuille par son identité stable', async ({ page }) => {
  await connectedFixture(page);
  await page.goto('/');
  await page.getByRole('button', { name: 'Ouvrir votre compagnon', exact: true }).click();
  await page.getByRole('button', { name: 'Agents 1', exact: true }).click();
  await page.getByRole('button', { name: 'Travailler sur cette feuille', exact: true }).click();
  await expect(page).toHaveURL(/\/expert\/feuilles\/stable-calendar/);
  await page.keyboard.press('Escape');
  await expect(page.getByRole('heading', { name: 'Calendrier du projet', exact: true })).toBeVisible();
});

test('cockpit réel : les courbes comparées partagent le calendrier et la même échelle sans inventer les mois manquants', async ({ page }, testInfo) => {
  const state = await connectedFixture(page);
  state.simulation.series = [{ id: 'cash', label: 'Trésorerie mensuelle', unit: 'EUR', status: 'CALCULE', categories: ['2026-02', '2026-03'], values: [90, 80] }];
  await page.route('**/api/**/scenarios/compare', route => route.fulfill({ json: { scenarios: [{ id: state.dossier.id, case_id: state.dossier.id, name: 'Référence', metrics: [], series: [{ id: 'cash', label: 'Trésorerie mensuelle', unit: 'EUR', status: 'CALCULE', categories: ['2026-01', '2026-02', '2026-03'], values: [100, null, 70] }] }] } }));
  await page.goto('/simulations/simulation-current');
  const chart = page.getByRole('img', { name: /Référence actuelle et simulation de trésorerie/ });
  await expect(chart).toBeVisible();
  const paths = await chart.locator('path').evaluateAll(elements => elements.map(element => element.getAttribute('d')));
  expect(paths).toHaveLength(2); expect(paths[0]?.match(/M/g)).toHaveLength(2); expect(paths[0]).not.toContain('L');
  await page.getByText('Comparer les montants mois par mois', { exact: true }).click();
  const table = page.getByRole('table', { name: 'Trésorerie comparée par mois' });
  await expect(table.getByRole('row').filter({ hasText: '2026-01' })).toContainText('Hors période');
  await expect(table.getByRole('row').filter({ hasText: '2026-02' })).toContainText('À compléter');
  await expect(table.getByRole('row').filter({ hasText: '2026-02' })).toContainText('90');
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.screenshot({ path: testInfo.outputPath('cockpit-comparaison.png'), fullPage: true });
});
