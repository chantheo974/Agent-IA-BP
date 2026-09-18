// Development-only acceptance: inspect the compiled cockpit served by the
// newly extracted package. No browser mutation, Excel job or AI request.
const { chromium, expect } = require('../frontend/node_modules/@playwright/test');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const [base, caseId, output] = process.argv.slice(2);
  assert.equal(new URL(base).hostname, '127.0.0.1');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ baseURL: base, viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  page.setDefaultTimeout(180000);
  const errors = [], responses = [], forbidden = [], spaces = [];
  const started = new Date().toISOString(), prefix = '/api/cases/' + caseId;
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => { if (response.url().includes('/api/')) responses.push({ path: new URL(response.url()).pathname, status: response.status() }); });
  await page.route('**/api/**', route => {
    if (route.request().method() !== 'GET') {
      forbidden.push({ method: route.request().method(), path: new URL(route.request().url()).pathname });
      return route.abort('blockedbyclient');
    }
    return route.continue();
  });
  try {
    const before = await (await context.request.get(prefix)).json();
    await page.addInitScript(id => localStorage.setItem('tca.case', id), caseId);
    await page.goto('/');
    await expect(page.getByLabel('Dossier actif')).toHaveValue(caseId, { timeout: 180000 });
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    const plan = [
      ['Entreprise', 'Personnaliser', 'Un espace à votre image'],
      ['Documents', 'Documents', 'Vos informations, avec leurs sources'],
      ['Prévisionnel', 'Parcours', 'Construisons votre prévisionnel'],
      ['Scénarios', 'Simulations', null],
      ['Réalisé', 'Suivi mensuel', 'Vos chiffres réels, vos prochaines décisions'],
      ['Livrables', 'Livrables', 'Partagez un dossier à jour'],
    ];
    for (const [label, destination, heading] of plan) {
      await page.getByRole('link', { name: destination, exact: true }).click();
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
      if (heading) await expect(page.getByRole('heading', { level: 1 })).toHaveText(heading);
      if (label === 'Entreprise') {
        await expect(page.getByLabel('Horizon du prévisionnel')).toHaveValue('2', { timeout: 180000 });
        await expect(page.getByLabel('Démarrage de l’activité')).toHaveValue('2026-04-01');
      }
      await expect(page.getByRole('button', { name: 'Ouvrir votre compagnon', exact: true })).toBeVisible();
      const screenshot = String(spaces.length + 1).padStart(2, '0') + '-cockpit.png';
      await page.screenshot({ path: path.join(output, screenshot), fullPage: true });
      spaces.push({ label, destination, heading, screenshot, status: 'PASS' });
    }
    await page.getByRole('link', { name: 'Mode expert', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Toutes les feuilles de votre modèle' })).toBeVisible();
    const catalog = await (await context.request.get(prefix + '/cockpit/catalog')).json();
    assert.equal(catalog.sheets.length, 33);
    const icon = await context.request.get('/icone/iconoir-sprite.svg');
    assert.equal(icon.status(), 200);
    assert.match(icon.headers()['content-type'], /svg/);
    const after = await (await context.request.get(prefix)).json();
    const jobs = await (await context.request.get(prefix + '/jobs')).json();
    assert.deepEqual(forbidden, []);
    assert.deepEqual(errors, []);
    assert.equal(after.revision, before.revision);
    assert.equal(after.sha256, before.sha256);
    assert.equal(jobs.jobs.length, 0);
    assert.ok(responses.every(response => response.status < 400), JSON.stringify(responses.filter(response => response.status >= 400)));
    const receipt = { status: 'PASS', started_at: started, finished_at: new Date().toISOString(), base_url: base, case_id: caseId,
      spaces, responses, browser_errors: errors, blocked_mutations: forbidden, real_sheets: catalog.sheets.length,
      financial_revision_before: before.revision, financial_revision_after: after.revision,
      workbook_sha256_before: before.sha256, workbook_sha256_after: after.sha256, jobs_created: 0,
      node_used_only_by_development_verifier: true, npm_invoked: false,
      limitations: ['Navigation en lecture seule sur le serveur du pack ; aucun calcul Excel ni appel IA.'] };
    await fs.writeFile(path.join(output, 'navigation-cockpit.json'), JSON.stringify(receipt, null, 2));
    console.log(JSON.stringify({ status: 'PASS', spaces_opened: spaces.length }));
  } catch (error) {
    await fs.writeFile(path.join(output, 'navigation-failure.json'), JSON.stringify({ error: error.stack || String(error), spaces, responses, forbidden, errors }, null, 2));
    await page.screenshot({ path: path.join(output, 'navigation-failure.png'), fullPage: true }).catch(() => {});
    throw error;
  } finally { await context.close(); await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
