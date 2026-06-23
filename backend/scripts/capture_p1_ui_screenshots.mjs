/**
 * Bounded UI screenshots for task_006 / task_003 (max ~3 min total).
 * Uses Playwright CLI package via dynamic import — NOT Cursor browser MCP.
 */
import { chromium } from "playwright";
import { mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, "..", "..", "docs", "screenshots");
mkdirSync(OUT, { recursive: true });

const BASE = "http://localhost:5173";

const TASKS = [
  {
    key: "task_006",
    before: "demo_p1_task006_ui_before.png",
    bad: "demo_p1_task006_ui_bad_submit.png",
    fixed: "demo_p1_task006_ui_fixed_submit.png",
    url: `${BASE}/tasks/4?learning_language=pascal&source_language=python`,
    badCode: `var n, i, load, total: integer;
begin
  readln(n);
  total := 0;
  for i := 1 to n do
  begin
    readln(load);
    total := total + load;
  end;
  writeln(total / n);
end.`,
    fixedCode: `var n, i, load, total: integer;
begin
  readln(n);
  total := 0;
  for i := 1 to n do
  begin
    readln(load);
    total := total + load;
  end;
  writeln(total div n);
end.`,
  },
  {
    key: "task_003",
    before: "demo_p1_task003_ui_before.png",
    bad: "demo_p1_task003_ui_bad_submit.png",
    fixed: "demo_p1_task003_ui_fixed_submit.png",
    url: `${BASE}/tasks/7?learning_language=pascal&source_language=python`,
    badCode: `var n, i, ping, best: integer;
begin
  readln(n);
  readln(ping);
  readln(ping);
  readln(ping);
  readln(ping);
  readln(ping);
  best := ping;
  writeln(best);
end.`,
    fixedCode: `var n, i, ping, best: integer;
begin
  readln(n);
  readln(best);
  for i := 2 to n do
  begin
    readln(ping);
    if ping < best then
      best := ping;
  end;
  writeln(best);
end.`,
  },
];

async function waitLoaded(page) {
  await page.waitForLoadState("domcontentloaded", { timeout: 25000 });
  await page.waitForSelector("h1", { timeout: 25000 });
  await page.waitForTimeout(4000);
}

async function trySetEditorCode(page, code) {
  const monaco = page.locator(".monaco-editor").first();
  if (await monaco.count()) {
    await monaco.click({ timeout: 5000 });
    await page.keyboard.press("Control+A");
    await page.keyboard.insertText(code);
    return true;
  }
  const ta = page.locator("textarea").first();
  if (await ta.count()) {
    await ta.fill(code);
    return true;
  }
  return false;
}

async function clickRun(page) {
  const btn = page.getByRole("button", { name: /прогнать|проверить|отправить/i });
  if (await btn.count()) {
    await btn.first().click({ timeout: 8000 });
    return true;
  }
  return false;
}

async function waitAfterSubmit(page) {
  await page.waitForTimeout(8000);
  const pitfall = page.getByText(/перенос|TRANSFER|алгоритм|ошибка/i);
  const tests = page.getByText(/\d+\s*\/\s*\d+/);
  await Promise.race([
    pitfall.first().waitFor({ state: "visible", timeout: 45000 }).catch(() => {}),
    tests.first().waitFor({ state: "visible", timeout: 45000 }).catch(() => {}),
    page.waitForTimeout(12000),
  ]);
}

async function captureTask(browser, task) {
  const page = await browser.newPage();
  page.setDefaultTimeout(20000);
  const result = { key: task.key, before: false, bad: false, fixed: false, notes: [] };
  try {
    await page.goto(task.url, { timeout: 30000 });
    await waitLoaded(page);
    await page.screenshot({ path: join(OUT, task.before), fullPage: true });
    result.before = true;

    if (await trySetEditorCode(page, task.badCode)) {
      if (await clickRun(page)) {
        await waitAfterSubmit(page);
        await page.screenshot({ path: join(OUT, task.bad), fullPage: true });
        result.bad = true;
      } else {
        result.notes.push("run button not found for bad");
      }
    } else {
      result.notes.push("editor not found for bad — assemble UI may use blocks only");
      await page.screenshot({ path: join(OUT, task.bad), fullPage: true });
      result.bad = true;
    }

    await page.goto(task.url, { timeout: 30000 });
    await waitLoaded(page);
    if (await trySetEditorCode(page, task.fixedCode)) {
      if (await clickRun(page)) {
        await waitAfterSubmit(page);
        await page.screenshot({ path: join(OUT, task.fixed), fullPage: true });
        result.fixed = true;
      } else {
        result.notes.push("run button not found for fixed");
      }
    } else {
      result.notes.push("editor not found for fixed");
    }
  } catch (e) {
    result.notes.push(String(e.message || e).slice(0, 200));
  } finally {
    await page.close();
  }
  return result;
}

const browser = await chromium.launch({ headless: true });
const results = [];
try {
  for (const task of TASKS) {
    results.push(await captureTask(browser, task));
  }
} finally {
  await browser.close();
}
console.log(JSON.stringify(results, null, 2));
