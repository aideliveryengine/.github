// Tira um print por passo do roteiro: abre a cena, aplica o estado e salva o PNG.
//   node video/prints.cjs tmp/plano.json 1920 1080
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const [plano, w, h] = [JSON.parse(fs.readFileSync(process.argv[2], 'utf8')), +process.argv[3], +process.argv[4]];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  let atual = null;
  for (const p of plano) {
    if (p.html !== atual) {
      await page.goto('file://' + p.html);
      await page.evaluate(() => document.fonts.ready);
      atual = p.html;
    }
    await page.evaluate((e) => window.estado(e), p.estado);
    await page.screenshot({ path: p.png });
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
