import { expect, test, type Page } from '@playwright/test';
import { mockWorkspace } from './fixture';

// Browser-only protocol fixture. It exercises real controls and SSE refreshes,
// but never calls Excel, an IA provider, or a real customer's dossier.
async function safetyFixture(page: Page) {
  const state = await mockWorkspace(page);
  const other = { ...state.case, id: 'other-safety-case', name: 'Autre dossier fictif' };
  const sheet = {
    id: 'safe-stable-calendar', name: 'Control', original_name: 'Control', label: 'Calendrier du projet',
    purpose: 'Hypothèses calendaires fictives', role: 'Calendrier', group_id: 'framework',
    theme_ids: ['synthesis'], view_kind: 'settings', field_count: 1, binding_count: 1,
    dependencies: [], dependency_basis: 'CONTRAT_METIER_VERSIONNE',
    fields: [{ field_id: 'year', label: 'Année de départ', value_type: 'integer', can_propose: true, binding_count: 1 }],
    register: { start_row: 10, end_row: 20, can_add: true },
  };
  await page.route('**/api/**', async route => {
    const request = route.request(), url = new URL(request.url()), path = url.pathname.slice(4);
    if (path === '/cases') return route.fulfill({ json: { cases: [state.case, other] } });
    if (path.endsWith('/profile')) return route.fulfill({ json: { profile: { name: 'Recette protection des saisies', start_year: 2026, years: 3 } } });
    if (path.endsWith('/cockpit/catalog')) return route.fulfill({ json: {
      schema: 'tca-cockpit/1', case_id: state.case.id, revision: state.case.revision,
      calculation_status: state.case.calculation_status, profile_version: 1, profile_sha256: 'fixture',
      groups: [{ id: 'framework', label: 'Cadre du projet' }], themes: [], sheets: [sheet],
    } });
    if (path.endsWith('/cockpit/sheets/' + sheet.id)) return route.fulfill({ json: {
      case_id: state.case.id, revision: state.case.revision, calculation_status: state.case.calculation_status,
      sheet, entries: [{ binding_id: 'safe-year', field_id: 'year', sheet_id: sheet.id, sheet: sheet.name,
        cell: 'C10', label: 'Année de départ', value: 2026, current_value: 2026, proposed: false,
        formula: null, value_type: 'integer', unit: 'année', status: 'HYPOTHESE', editable: true, calculated: false }],
      total: 1, offset: 0, limit: 100, draft: { status: 'EMPTY', current: true },
    } });
    if (path.endsWith('/cockpit/cells')) {
      const top = Number(url.searchParams.get('row')), left = Number(url.searchParams.get('column'));
      const rows = Number(url.searchParams.get('rows')), columns = Number(url.searchParams.get('columns'));
      const cells = [];
      for (let row = top; row < top + rows; row++) for (let column = left; column < left + columns; column++) {
        let n = column, letters = '';
        while (n > 0) { n--; letters = String.fromCharCode(65 + n % 26) + letters; n = Math.floor(n / 26); }
        const cell = letters + row;
        cells.push({ cell, row, column, value: cell === 'C10' ? 2026 : null, formula: null, editable: cell === 'C10' });
      }
      return route.fulfill({ json: { sheet: sheet.name, revision: state.case.revision, cells } });
    }
    if (path.endsWith('/cockpit/operations')) {
      const body = request.postDataJSON();
      state.requests.push({ path, method: request.method(), body });
      if (body.expected_revision !== state.case.revision) return route.fulfill({ status: 409, json: { detail: 'Révision périmée' } });
      state.draft = { ...state.draft, status: 'DRAFT', operations: body.operations };
      return route.fulfill({ json: state.draft });
    }
    return route.fallback();
  });
  return { state, sheet, other };
}

async function openGrid(page: Page, sheetId: string) {
  await page.goto('/expert/feuilles/' + sheetId + '?vue=grille');
  await page.getByLabel('Source de la saisie', { exact: true }).selectOption('source-1');
  await page.getByLabel('Adresse de cellule', { exact: true }).fill('C10');
  await page.getByLabel('Adresse de cellule', { exact: true }).press('Enter');
  const input = page.getByLabel('Valeur ou formule de la cellule', { exact: true });
  await expect(input).toBeEnabled();
  await expect(input).toHaveValue('2026');
  await expect(page.getByTestId('data-grid-canvas')).toBeVisible();
}

test('sécurité cockpit : un profil reçu après la sélection ne reprend pas le focus de la grille', async ({ page }) => {
  const { sheet } = await safetyFixture(page);
  let releaseProfile!: () => void;
  const profileGate = new Promise<void>(resolve => { releaseProfile = resolve; });
  await page.route('**/api/cases/*/profile', async route => {
    await profileGate;
    await route.fallback();
  });
  try {
    await openGrid(page, sheet.id);
    const canvas = page.getByTestId('data-grid-canvas');
    await canvas.focus();
    await expect(canvas).toBeFocused();
    releaseProfile();
    await expect(page).toHaveTitle('Mode expert · Recette protection des saisies');
    await expect(canvas).toBeFocused();
  } finally {
    releaseProfile();
  }
});

test('sécurité cockpit : une opération en cours ne disparaît pas lors de la navigation ou du changement de dossier refusés', async ({ page }) => {
  const { state, sheet, other } = await safetyFixture(page);
  await page.goto('/expert/feuilles/' + sheet.id);
  const entry = page.getByLabel('Nouvelle opération · Année de départ', { exact: true });
  await entry.fill('2031');
  const dialogs: string[] = [];
  page.on('dialog', async dialog => { dialogs.push(dialog.message()); await dialog.dismiss(); });
  await page.getByRole('button', { name: 'Toutes les feuilles', exact: true }).click();
  await expect.poll(() => dialogs.length).toBe(1);
  await expect(page).toHaveURL(new RegExp('/expert/feuilles/' + sheet.id));
  await expect(entry).toHaveValue('2031');
  await page.getByLabel('Dossier actif', { exact: true }).selectOption(other.id);
  await expect.poll(() => dialogs.length).toBe(2);
  await expect(page.getByLabel('Dossier actif', { exact: true })).toHaveValue(state.case.id);
  await expect(entry).toHaveValue('2031');
  expect(state.requests.filter(request => request.method === 'POST')).toHaveLength(0);
});

test('sécurité cockpit : une saisie de grille commencée avant une nouvelle révision ne se rattache pas silencieusement à celle-ci', async ({ page }) => {
  const { state, sheet } = await safetyFixture(page);
  await openGrid(page, sheet.id);
  const input = page.getByLabel('Valeur ou formule de la cellule', { exact: true });
  await input.fill('2029');
  state.case.revision = 1;
  // Wait for App's authoritative revision, not a detail query that may finish
  // earlier while refreshCase is still gathering its other HTTP responses.
  await expect(page.locator('.reference-mini-card')).toContainText('Révision 1', { timeout: 20000 });
  await expect(input).toHaveValue('2029');
  await page.getByRole('button', { name: 'Ajouter la valeur au brouillon', exact: true }).click();
  await expect(page.getByRole('alert').filter({ hasText: /révision|changé|périm/i }).first()).toBeVisible();
  await expect(input).toHaveValue('2029');
  expect(state.requests.filter(request => request.path.endsWith('/cockpit/operations'))).toHaveLength(0);
  expect(state.draft.operations).toHaveLength(0);
});

test('sécurité cockpit : un collage en attente garde sa révision et ses valeurs après actualisation', async ({ page, context }) => {
  const { state, sheet } = await safetyFixture(page);
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await openGrid(page, sheet.id);
  await page.evaluate(() => navigator.clipboard.writeText('2032'));
  await expect.poll(() => page.evaluate(() => navigator.clipboard.readText())).toBe('2032');
  const canvas = page.getByTestId('data-grid-canvas');
  await canvas.focus();
  await expect(canvas).toBeFocused();
  await page.keyboard.press('Control+v');
  const dialog = page.getByRole('dialog', { name: 'Vérifier le collage', exact: true });
  await expect(dialog).toBeVisible();
  state.case.revision = 1;
  // The modal makes the content inert, but server refreshes must still advance
  // the dossier while preserving this already captured paste intention.
  await expect(page.locator('.reference-mini-card')).toContainText('Révision 1', { timeout: 20000 });
  await page.getByRole('button', { name: 'Ajouter le collage au brouillon', exact: true }).click();
  await expect(page.getByRole('alert').filter({ hasText: /révision|changé|périm/i }).first()).toBeVisible();
  await expect(dialog).toBeVisible();
  await expect(dialog.locator('tbody')).toContainText('2032');
  expect(state.requests.filter(request => request.path.endsWith('/cockpit/operations'))).toHaveLength(0);
  expect(state.draft.operations).toHaveLength(0);
});
