import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { performance } from 'node:perf_hooks';
import process from 'node:process';

const candidate = process.env.BROWSER_CANDIDATE;
if (!['playwright-node', 'patchright-node'].includes(candidate)) throw new Error(`Unsupported candidate: ${candidate}`);
const pkg = candidate === 'playwright-node' ? 'playwright' : 'patchright';
const { chromium } = await import(pkg);

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'web2api-runtime-'));
const profileA = path.join(root, 'profile-a');
const profileB = path.join(root, 'profile-b');
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  if (url.pathname === '/api/echo') {
    res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify({ request_id: url.searchParams.get('request_id'), observed: true }));
    return;
  }
  res.setHeader('content-type', 'text/html');
  res.end(`<!doctype html><button id="action">Run request</button><output id="state">0</output><script>
    document.querySelector('#action').addEventListener('click', async () => {
      const id = crypto.randomUUID();
      const r = await fetch('/api/echo?request_id=' + id);
      const j = await r.json();
      localStorage.setItem('request_id', j.request_id);
      document.querySelector('#state').textContent = j.observed ? '1' : '0';
    });
  </script>`);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const result = { candidate, checks: {}, timings_ms: {}, rss_mb: process.memoryUsage().rss / 1024 / 1024 };
let browser;
try {
  let t = performance.now();
  let context = await chromium.launchPersistentContext(profileA, { headless: true });
  result.timings_ms.first_launch = performance.now() - t;
  const page = await context.newPage();
  await page.goto(base);
  await page.getByRole('button', { name: 'Run request' }).click();
  await page.locator('#state').waitFor({ state: 'visible' });
  result.checks.semantic_interaction = (await page.locator('#state').textContent()) === '1';
  result.checks.request_correlation = Boolean(await page.evaluate(() => localStorage.getItem('request_id')));
  await context.close();
  t = performance.now();
  context = await chromium.launchPersistentContext(profileA, { headless: true });
  result.timings_ms.restart = performance.now() - t;
  const page2 = await context.newPage();
  await page2.goto(base);
  result.checks.persistence = Boolean(await page2.evaluate(() => localStorage.getItem('request_id')));
  await context.close();
  context = await chromium.launchPersistentContext(profileB, { headless: true });
  const pageB = await context.newPage();
  await pageB.goto(base);
  result.checks.profile_isolation = !(await pageB.evaluate(() => localStorage.getItem('request_id')));
  await context.close();
  result.checks.all_pass = Object.values(result.checks).every(Boolean);
  console.log(JSON.stringify(result, null, 2));
  if (!result.checks.all_pass) process.exitCode = 1;
} finally {
  if (browser) await browser.close().catch(() => {});
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(root, { recursive: true, force: true });
}
