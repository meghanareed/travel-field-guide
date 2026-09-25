#!/usr/bin/env node
/* Headless smoke test for a built field-guide app.

     node validate.js path/to/index.html [--shots outdir]

   Clicks every tab and every day, toggles a Seen pill + a packing check and
   confirms they survive a reload, and fails on any console/page error.
   Needs Playwright (npm i -g playwright, or NODE_PATH pointing at it). If the
   bundled browser isn't installed, set PW_CHROMIUM=/path/to/chromium. */
const path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); }
catch (e) { ({ chromium } = require(require("child_process").execSync("npm root -g").toString().trim() + "/playwright")); }

const file = path.resolve(process.argv[2] || "index.html");
const shotsIdx = process.argv.indexOf("--shots");
const shots = shotsIdx > 0 ? process.argv[shotsIdx + 1] : null;
const fail = [];
const ok = (cond, msg) => { if (!cond) fail.push(msg); };

(async () => {
  const opts = process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {};
  const browser = await chromium.launch(opts);
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", x => errors.push(String(x)));
  await page.goto("file://" + file);
  await page.waitForTimeout(300);

  for (const t of ["Today", "Days", "Places", "Lists", "Info"]) {
    await page.click(`nav >> text=${t}`);
    await page.waitForTimeout(60);
    ok((await page.locator("#app .view").count()) === 1, `${t} tab did not render`);
    if (shots) await page.screenshot({ path: `${shots}/${t.toLowerCase()}.png`, fullPage: true });
  }

  // every day opens; stop numbering is 1..K with transit rows unnumbered
  await page.click("nav >> text=Days");
  const n = await page.locator(".daycard").count();
  ok(n > 0, "no day cards");
  const nDays = await page.evaluate(() => DATA.days.length);
  ok(n === nDays, `day cards (${n}) != DATA.days (${nDays})`);
  let firstTourDay = null;
  for (let i = 0; i < n; i++) {
    await page.evaluate(d => go("days", { day: d }), i + 1);
    await page.waitForTimeout(30);
    const nums = await page.locator(".stop .num").allTextContents();
    nums.forEach((v, k) => ok(v === String(k + 1), `day ${i + 1}: stop numbers not 1..K (${nums.join(",")})`));
    const real = await page.evaluate(d => (DATA.days[d - 1].tour?.stops || []).filter(s => !s.transit).length, i + 1);
    ok(nums.length === real, `day ${i + 1}: rendered ${nums.length} stops, data has ${real}`);
    if (real && firstTourDay === null) firstTourDay = i + 1;
  }

  // persistence: Seen toggle + packing check survive reload
  if (firstTourDay) {
    await page.evaluate(d => go("days", { day: d }), firstTourDay);
    await page.locator(".seentog").first().click();
  }
  const hasPack = await page.evaluate(() => (DATA.packing || []).length > 0);
  if (hasPack) {
    await page.click("nav >> text=Lists");
    await page.locator(".check").first().click();
  }
  await page.reload();
  await page.waitForTimeout(300);
  if (firstTourDay) {
    await page.evaluate(d => go("days", { day: d }), firstTourDay);
    ok(await page.locator(".seentog.on").count() === 1, "Seen toggle did not persist");
  }
  if (hasPack) {
    await page.click("nav >> text=Lists");
    ok(await page.locator(".check.on").count() === 1, "packing check did not persist");
  }
  // shopping switcher, if any
  const hasShop = await page.evaluate(() => SHOPPING.lists.length > 0);
  if (hasShop) {
    await page.evaluate(() => switchListMode("shop"));
    ok(await page.locator(".tier-head").count() > 0, "shopping list did not render");
  }
  await page.evaluate(() => localStorage.clear());
  await browser.close();

  errors.forEach(e => fail.push("console: " + e));
  if (fail.length) { console.error("FAIL\n  " + fail.join("\n  ")); process.exit(1); }
  console.log(`OK — ${n} days, all tabs render, no console errors`);
})().catch(e => { console.error(e); process.exit(1); });
