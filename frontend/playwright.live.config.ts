import { defineConfig } from "@playwright/test";
import { tmpdir } from "node:os";
import { join } from "node:path";
if (!process.env.TCA_WEB_LIVE_URL) throw new Error("Définir TCA_WEB_LIVE_URL vers un serveur de recette isolé. Ce test crée un dossier fictif, une source et un brouillon.");
// The config also runs inside each worker. Keep one artifact directory for the
// whole invocation, including cleanup and traces produced during teardown.
const runId = process.env.TCA_WEB_LIVE_RUN_ID ||= new Date().toISOString().replace(/[:.]/g, "-");
export default defineConfig({
  testDir: "./tests", testMatch: "live*.spec.ts", workers: 1, timeout: 180000,
  expect: { timeout: 45000 }, reporter: [["list"], ["json", { outputFile: "test-results/live-results.json" }]],
  outputDir: "test-results/live-" + runId,
  use: { baseURL: process.env.TCA_WEB_LIVE_URL, browserName: "chromium", viewport: { width: 1440, height: 1000 }, screenshot: "only-on-failure", trace: "retain-on-failure", acceptDownloads: true, launchOptions: { downloadsPath: join(tmpdir(), "tca-web-browser-" + Date.now()) } },
});
