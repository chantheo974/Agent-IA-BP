import { expect, test } from '@playwright/test';
import fs from 'node:fs/promises';
import type { Catalog } from '../src/connected/types';
import type { SheetOutputSnapshot } from '../src/connected/SheetOutputs';

// Read-only witness for the documented fictitious 24 kEUR native Excel recipe.
// The case is supplied explicitly; this test never creates or adopts anything.
test('sorties calculées et navigateur réels : reconnaissance, facturation, encaissement, trésorerie et annuels', async ({ page }, info) => {
  const caseId = process.env.TCA_COCKPIT_NATIVE_CASE;
  test.skip(!caseId, 'TCA_COCKPIT_NATIVE_CASE doit identifier la copie fictive calculée de la recette 24 kEUR.');
  const base = '/api/cases/' + encodeURIComponent(caseId!);
  const errors: string[] = [], mutations: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (request.url().includes('/api/') && request.method() !== 'GET') mutations.push(request.method() + ' ' + new URL(request.url()).pathname); });
  const before = await (await page.request.get(base)).json();
  expect(before.outputs_current).toBe(true);
  const jobsBefore = (await (await page.request.get(base + '/jobs')).json()).jobs;
  const catalog = await (await page.request.get(base + '/cockpit/catalog')).json() as Catalog;
  const revenue = catalog.sheets.find(sheet => sheet.original_name === 'Revenue');
  const financial = catalog.sheets.find(sheet => sheet.original_name === 'Modèle financier');
  expect(revenue).toBeTruthy(); expect(financial).toBeTruthy();
  await page.addInitScript(id => localStorage.setItem('tca.case', id), caseId!);

  async function openOutputs(sheetId: string) {
    const outputResponse = page.waitForResponse(response => response.url().endsWith('/cockpit/sheets/' + sheetId + '/outputs'));
    await page.goto('/expert/feuilles/' + sheetId);
    const response = await outputResponse;
    expect(response.status(), await response.text()).toBe(200);
    const output = await response.json() as SheetOutputSnapshot;
    expect(output).toMatchObject({ case_id: caseId, revision: before.revision, sha256: before.sha256, outputs_current: true, sheet_id: sheetId });
    return output;
  }
  const revenueOutput = await openOutputs(revenue!.id);
  expect(revenueOutput.series.map(series => series.id)).toEqual(['revenue', 'billed_revenue', 'customer_receipts']);
  await page.getByLabel('Année des séries mensuelles', { exact: true }).selectOption('2026');
  const monthly = page.getByRole('table', { name: 'Résultats mensuels de la feuille' });
  async function rowValues(period: string, expected: number[]) {
    const row = monthly.getByRole('row').filter({ hasText: period });
    for (let index = 0; index < expected.length; index++) {
      const actual = (await row.getByRole('cell').nth(index).innerText()).split('\n')[0];
      expect(actual).toBe(expected[index].toLocaleString('fr-FR', { maximumFractionDigits: 2 }) + ' €');
    }
  }
  await rowValues('2026-11', [8000, 12000, 0]);
  await rowValues('2026-12', [8000, 0, 12000]);
  await expect(monthly).toContainText('Revenue ·');
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.screenshot({ path: info.outputPath('cockpit-revenue-calcul-excel-reel.png'), fullPage: true });
  await page.getByLabel('Année des séries mensuelles', { exact: true }).selectOption('2027');
  await rowValues('2027-01', [8000, 0, 0]);

  const financialOutput = await openOutputs(financial!.id);
  await page.getByLabel('Année des séries mensuelles', { exact: true }).selectOption('2026');
  await rowValues('2026-11', [100000, 0, 0]);
  await rowValues('2026-12', [112000, 12000, 0]);
  const annual = page.getByRole('table', { name: 'Résultats annuels de la feuille' });
  await expect(annual.getByRole('row').filter({ hasText: 'Chiffre d’affaires — 2026' })).toContainText(/16[\s\u202f]000 €/);
  await expect(annual.getByRole('row').filter({ hasText: 'Chiffre d’affaires — 2027' })).toContainText(/8[\s\u202f]000 €/);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.screenshot({ path: info.outputPath('cockpit-tresorerie-annuels-excel-reel.png'), fullPage: true });
  await page.getByLabel('Année des séries mensuelles', { exact: true }).selectOption('2027');
  await rowValues('2027-05', [124000, 12000, 0]);
  const after = await (await page.request.get(base)).json();
  const jobsAfter = (await (await page.request.get(base + '/jobs')).json()).jobs;
  expect(after.revision).toBe(before.revision); expect(after.sha256).toBe(before.sha256);
  expect(jobsAfter.map((job: { id: string }) => job.id)).toEqual(jobsBefore.map((job: { id: string }) => job.id));
  expect(mutations).toEqual([]); expect(errors).toEqual([]);
  await fs.writeFile(info.outputPath('receipt.json'), JSON.stringify({ status: 'PASS_REAL_CALCULATED_COCKPIT_READ_ONLY', case_id: caseId, before: { revision: before.revision, sha256: before.sha256 }, after: { revision: after.revision, sha256: after.sha256 }, revenue_sheet_id: revenue!.id, cash_sheet_id: financial!.id, revenue_output: revenueOutput, financial_output: financialOutput, browser_mutations: mutations, browser_errors: errors, limits: ['Fictitious 24 kEUR native recipe only; this browser run performs no write, recalculation or IA provider call.'] }, null, 2));
});
