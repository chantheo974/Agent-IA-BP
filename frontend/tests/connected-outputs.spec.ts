import { expect, test, type Page } from '@playwright/test';
import { mockWorkspace } from './fixture';
import type { SheetOutputSnapshot } from '../src/connected/SheetOutputs';

async function outputFixture(page: Page, original = 'Revenue') {
  const state = await mockWorkspace(page);
  const provenance = { case_id: state.case.id, revision: 0, sha256: 'current-workbook' };
  const sheet = { id: 'stable-output-sheet', name: original + ' renommé', original_name: original, label: original === 'Revenue' ? 'Revenus et encaissements clients' : 'Résultats annuels', purpose: 'Sorties réelles du moteur dans une réponse API simulée.', role: 'Sorties', group_id: 'statements', theme_ids: ['synthesis'], view_kind: 'series', field_count: 0, binding_count: 0, dependencies: [], dependency_basis: 'CONTRAT_METIER_VERSIONNE', fields: [], register: null };
  const labels = ['Chiffre d’affaires reconnu', 'Facturation clients', 'Encaissements clients'];
  const values = [[1250, 1500, null], [2000, 0, 500], [0, 2000, null]];
  const output: SheetOutputSnapshot = {
    schema: 'tca-cockpit-outputs/1', ...provenance, profile_sha256: 'current-profile', calculation_status: 'RECALCULE', outputs_current: true, sheet_id: sheet.id, metrics: [], annual_metrics: [], diagnostics: [],
    series: ['revenue', 'billed_revenue', 'customer_receipts'].map((id, index) => ({ id, label: labels[index], unit: 'EUR', status: 'DISPONIBLE_SUR_PREREQUIS_QUALIFIES', available: true, provenance: { ...provenance }, qualification: { scenario_ready: true }, case_id: state.case.id, revision: 0, categories: ['2026-01', '2026-02', '2026-03'], values: values[index], sources: ['P', 'Q', 'R'].map(column => ({ sheet: sheet.name, cell: column + (282 + index) })) })),
  };
  await page.route('**/api/**', async route => {
    const path = new URL(route.request().url()).pathname.slice(4);
    if (path === '/cases/' + state.case.id) return route.fulfill({ json: { ...state.case, sha256: provenance.sha256, calculation_status: 'RECALCULE' } });
    if (path.endsWith('/profile')) return route.fulfill({ json: { profile: { name: 'Dossier fictif de sorties' } } });
    if (path.endsWith('/sheets')) return route.fulfill({ json: { sheets: [{ name: sheet.name, rows: 330, columns: 135 }] } });
    if (path.endsWith('/cockpit/catalog')) return route.fulfill({ json: { schema: 'tca-cockpit/1', ...provenance, profile_sha256: 'current-profile', profile_version: '1', calculation_status: 'RECALCULE', groups: [{ id: 'statements', label: 'Résultats' }], themes: [], sheets: [sheet] } });
    if (path.endsWith('/cockpit/sheets/' + sheet.id)) return route.fulfill({ json: { ...provenance, calculation_status: 'RECALCULE', sheet, entries: [], total: 0, offset: 0, limit: 100, draft: { status: 'EMPTY', current: true } } });
    if (path.endsWith('/cockpit/sheets/' + sheet.id + '/outputs')) return route.fulfill({ json: output });
    return route.fallback();
  });
  return { state, output, sheet, provenance };
}

test('sorties cockpit : revenu reconnu, facturé et encaissé restent distincts, sourcés et sans zéro implicite', async ({ page }, info) => {
  const { sheet } = await outputFixture(page);
  await page.goto('/expert/feuilles/' + sheet.id);
  const table = page.getByRole('table', { name: 'Résultats mensuels de la feuille' });
  await expect(table.getByRole('columnheader', { name: /Chiffre d’affaires reconnu/ })).toBeVisible();
  await expect(table.getByRole('columnheader', { name: /Facturation clients/ })).toBeVisible();
  await expect(table.getByRole('columnheader', { name: /Encaissements clients/ })).toBeVisible();
  const january = table.getByRole('row').filter({ hasText: '2026-01' });
  await expect(january.getByRole('cell').nth(0)).toContainText(/1[\s\u202f]250 €/);
  await expect(january.getByRole('cell').nth(1)).toContainText(/2[\s\u202f]000 €/);
  await expect(january.getByRole('cell').nth(2)).toContainText('0 €');
  await expect(table.getByRole('row').filter({ hasText: '2026-03' }).getByRole('cell').nth(0)).toContainText('À compléter');
  await page.screenshot({ path: info.outputPath('cockpit-revenus-sources.png'), fullPage: true });
  await table.getByRole('button', { name: 'Cellule de calcul · Chiffre d’affaires reconnu · 2026-01', exact: true }).click();
  await expect(page).toHaveURL(/\/expert\/feuilles\/stable-output-sheet\?vue=grille&cell=P282/);
});

test('sorties cockpit : les résultats annuels conservent période, euros, qualification et cellule', async ({ page }) => {
  const { output, sheet, provenance } = await outputFixture(page, 'Compte de Résultat');
  output.series = [];
  output.annual_metrics = [{ id: 'gross_margin_2027', metric: 'gross_margin', label: 'Marge brute — 2027', period: '2027', value: 14250, unit: 'EUR', available: true, status: 'HYPOTHESES_A_CONFIRMER', provenance, qualification: { scenario_ready: true, hypotheses: [{ message: 'Prix de vente à confirmer avec une source.' }] }, sheet: sheet.name, cell: 'E25' }];
  await page.goto('/expert/feuilles/' + sheet.id);
  const table = page.getByRole('table', { name: 'Résultats annuels de la feuille' });
  await expect(table).toContainText('Marge brute — 2027');
  await expect(table).toContainText(/14[\s\u202f]250 €/);
  await expect(table).toContainText('E25');
  await expect(table).not.toContainText('%');
  await page.getByText('Qualifications et hypothèses à examiner (1)', { exact: true }).click();
  await expect(page.getByText('Prix de vente à confirmer avec une source.', { exact: true })).toBeVisible();
});

test('sorties cockpit : un calcul périmé ne montre aucune ancienne valeur', async ({ page }) => {
  const { output, sheet } = await outputFixture(page);
  output.outputs_current = false;
  await page.goto('/expert/feuilles/' + sheet.id);
  await expect(page.getByText(/Les calculs de cette révision doivent être actualisés/)).toBeVisible();
  const table = page.getByRole('table', { name: 'Résultats mensuels de la feuille' });
  await expect(table).toContainText('Indisponible');
  await expect(table).not.toContainText(/1[\s\u202f]250/);
  await expect(table).not.toContainText('0 €');
});

for (const mismatch of ['revision', 'sha256', 'profile', 'provenance'] as const) {
  test('sorties cockpit : un résultat de mauvaise ' + mismatch + ' est masqué', async ({ page }) => {
    const { output, sheet } = await outputFixture(page);
    if (mismatch === 'revision') output.revision = 1;
    if (mismatch === 'sha256') output.sha256 = 'other-workbook';
    if (mismatch === 'profile') output.profile_sha256 = 'other-profile';
    if (mismatch === 'provenance') output.series[0].provenance = { ...output.series[0].provenance, case_id: 'other-case' };
    await page.goto('/expert/feuilles/' + sheet.id);
    await expect(page.getByRole('alert').filter({ hasText: /ne correspondent pas à la révision courante/ })).toBeVisible();
    await expect(page.getByRole('table', { name: 'Résultats mensuels de la feuille' })).toHaveCount(0);
  });
}

test('sorties cockpit : une qualification bloquée reste explicite et une feuille non couverte garde son accès à la grille', async ({ page }) => {
  const { output, sheet } = await outputFixture(page);
  output.series.forEach(item => { item.available = false; item.qualification = { scenario_ready: false, blockers: [{ message: 'Le calendrier de reconnaissance reste à qualifier.' }] }; });
  await page.goto('/expert/feuilles/' + sheet.id);
  const table = page.getByRole('table', { name: 'Résultats mensuels de la feuille' });
  await expect(table).toContainText('Indisponible');
  await expect(table).not.toContainText(/1[\s\u202f]250/);
  await page.getByText('Qualifications et hypothèses à examiner (1)', { exact: true }).click();
  await expect(page.getByText('Le calendrier de reconnaissance reste à qualifier.', { exact: true })).toBeVisible();
  output.series = [];
  output.diagnostics = ['Projection structurée non homologuée pour cette feuille.'];
  await page.reload();
  await expect(page.getByText(/cette limitation ne signifie pas que le classeur est vide/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Consulter la grille de cette feuille', exact: true })).toBeVisible();
});
