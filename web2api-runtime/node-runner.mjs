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
let context;
try {
  let t = performance.now();
  context = await chromium.launchPersistentContext(profileA, { headless: true });
  result.timings_ms.first_launch = performance.now() - t;
  const page = await context.newPage();
  await page.goto(base);
  await page.getByRole('button', { name: 'Run request' }).click();
  await page.locator('#state').waitFor({ state: 'visible' });
  const requestId = await page.evaluate(() => localStorage.getItem('request_id'));
  result.checks.semantic_interaction = (await page.locator('#state').textContent()) === '1';
  result.checks.request_correlation = typeof requestId === 'string' && requestId.length >= 16;
  let timedOut = false;
  try { await page.locator('#never-exists').waitFor({ state: 'visible', timeout: 100 }); } catch { timedOut = true; }
  result.checks.timeout_detection = timedOut;
  await context.close();
  context = undefined;

  t = performance.now();
  context = await chromium.launchPersistentContext(profileA, { headless: true });
  result.timings_ms.restart = performance.now() - t;
  const page2 = await context.newPage();
  await page2.goto(base);
  result.checks.persistence = Boolean(await page2.evaluate(() => localStorage.getItem('request_id')));
  await context.close();
  context = undefined;

  context = await chromium.launchPersistentContext(profileB, { headless: true });
  const pageB = await context.newPage();
  await pageB.goto(base);
  result.checks.profile_isolation = !(await pageB.evaluate(() => localStorage.getItem('request_id')));
  await context.close();
  context = undefined;

  context = await chromium.launchPersistentContext(profileA, { headless: true });
  const disconnectedPage = await context.newPage();
  await disconnectedPage.goto(base);
  await context.close();
  context = undefined;
  let disconnected = false;
  try { await disconnectedPage.title(); } catch { disconnected = true; }
  result.checks.closed_browser_detection = disconnected;

  result.checks.all_pass = Object.values(result.checks).every(Boolean);
  console.log(JSON.stringify(result, null, 2));
  if (!result.checks.all_pass) process.exitCode = 1;
} finally {
  if (context) await context.close().catch(() => {});
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(root, { recursive: true, force: true });
}
