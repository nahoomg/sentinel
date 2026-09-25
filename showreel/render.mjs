// Frame-accurate offline render of index.html → frames/*.png
// usage: node render.mjs [outDir] [fps] [t0] [t1]
import { chromium } from 'playwright-core';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const out = process.argv[2] || path.join(here, 'frames');
const fps = Number(process.argv[3] || 60);
const t0 = Number(process.argv[4] || 0), t1 = Number(process.argv[5] || 15);
mkdirSync(out, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--allow-file-access-from-files'],
});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('console', m => console.log('[page]', m.text()));
page.on('pageerror', e => { console.error('[pageerror]', e); process.exit(1); });
await page.goto(pathToFileURL(path.join(here, 'index.html')).href + '?render');
await page.waitForFunction(() => window.READY === true);

const first = Math.round(t0 * fps), last = Math.round(t1 * fps);
for (let f = first; f < last; f++) {
  await page.evaluate(t => window.renderFrame(t), f / fps);
  const png = await page.screenshot({ type: 'png', clip: { x: 0, y: 0, width: 1920, height: 1080 } });
  writeFileSync(path.join(out, `f${String(f).padStart(4, '0')}.png`), png);
  if (f % 60 === 0) console.log(`frame ${f}/${last}`);
}
await browser.close();
