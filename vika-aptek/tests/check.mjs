// Проверка собранного файла в Chromium (Playwright): node tests/check.mjs
// Офлайн, ссылки, ширина телефона, тёмная тема, тренажёр от начала до конца, экспорт/импорт.
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';

const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const fileUrl = pathToFileURL(join(root, 'dist', 'vika-aptek.html')).href;
const shots = process.env.SHOTS || join(root, 'tests', 'shots');
mkdirSync(shots, { recursive: true });

let fails = 0;
const ok = (c, m) => { if (c) console.log('  ✓ ' + m); else { fails++; console.log('  ✗ ' + m); } };

const browser = await pw.chromium.launch({ executablePath: process.env.CHROME || undefined });
const ctx = await browser.newContext({ viewport: { width: 375, height: 760 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, acceptDownloads: true });
await ctx.setOffline(true);
const external = [];
await ctx.route('**/*', r => { const u = r.request().url(); if (!u.startsWith('file:') && !u.startsWith('data:') && !u.startsWith('blob:')) { external.push(u); return r.abort(); } return r.continue(); });
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', e => errors.push(e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('dialog', d => d.accept());

const go = async h => { await page.evaluate(x => { location.hash = x; }, h); await page.waitForTimeout(60); };

console.log('1. Загрузка офлайн');
await page.goto(fileUrl);
ok(await page.locator('h1').first().isVisible(), 'главная открылась без сети');

console.log('2. Все страницы и ссылки');
const seen = new Set(), queue = ['#/'];
while (queue.length) {
  const h = queue.shift(); if (seen.has(h)) continue; seen.add(h);
  await go(h);
  const title = await page.locator('h1').first().textContent();
  if (title.includes('не найдена')) { fails++; console.log('  ✗ битая ссылка ' + h); }
  const notes = await page.locator('.notice.model').count() + await page.locator('.notice.med').count();
  if (notes !== 2) { fails++; console.log('  ✗ нет плашек-напоминаний на ' + h); }
  const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  if (over > 1) { fails++; console.log('  ✗ горизонтальная прокрутка на ' + h + ': ' + over + 'px'); }
  const links = await page.$$eval('a[href^="#/"]', as => as.map(a => a.getAttribute('href')));
  links.forEach(l => { if (!seen.has(l) && !/\/(hints|nohints)$/.test(l)) queue.push(l); });
  const ext = await page.$$eval('a[href]', as => as.map(a => a.getAttribute('href')).filter(h => !h.startsWith('#')));
  if (ext.length) { fails++; console.log('  ✗ внешние ссылки на ' + h + ': ' + ext.join(', ')); }
}
ok(seen.size > 40, 'обойдено страниц: ' + seen.size);

console.log('3. Урок и тест');
await go('#/lesson/what');
for (let i = 0; i < 6; i++) {
  const q = await page.locator('.q').textContent();
  const btns = page.locator('.opt');
  const n = await btns.count();
  // ответ берём из данных
  const right = await page.evaluate(qt => { const q = VA.lessons[0].quiz.find(x => x.q === qt); return q.a[q.c]; }, q);
  for (let k = 0; k < n; k++) if ((await btns.nth(k).textContent()) === right) { await btns.nth(k).click(); break; }
  await page.locator('.next').click();
}
ok((await page.locator('#quiz h2').textContent()).includes('6 из 6'), 'тест урока пройден на 6/6');
ok(await page.evaluate(() => JSON.parse(localStorage.getItem('vika-aptek-v1')).lessons.what.done === true), 'прогресс урока сохранён');

console.log('4. Тренажёр с подсказками — все сценарии');
async function search(mode, q) {
  await page.locator('.seg button', { hasText: mode }).click();
  await page.fill('input[type=search]', q);
  await page.locator('button[type=submit]', { hasText: 'Найти' }).click();
}
async function openRes(text) { await page.locator('.result', { hasText: text }).first().click(); }
async function addLot(lot, qty) { await page.locator('label.lot', { hasText: lot }).locator('input').check(); await page.fill('#qtyIn', String(qty)); await page.locator('[data-act=add]').click(); }
const done = async (name) => { const t = await page.locator('#trainerHost h2').nth(1).textContent().catch(() => ''); ok(t.includes('без ошибок'), name + ': ' + t); };

await go('#/trainer/find/hints');
await search('МНН', 'усл'); await openRes('шипучие'); await addLot('УУ-0377', 1);
await page.locator('[data-act=scan]').click(); await done('Найти товар');

await go('#/trainer/sale/hints');
await search('Штрихкод', '2000000000011'); await openRes('Термоглин 500'); await addLot('ТГ-2207', 2);
await search('Название', 'плас'); await openRes('Пластырь'); await addLot('ПЛ-12', 1);
await page.locator('[data-act=scan]').click();
ok(await page.locator('text=Код маркировки не считывается').isVisible(), 'появился вопрос о нечитаемом коде');
await page.locator('[data-act=choice][data-v=retry]').click();
await page.locator('[data-act=scan]').click();
await page.screenshot({ path: join(shots, 'trainer-sale.png'), fullPage: true });
await page.locator('[data-act=pay][data-v=card]').click(); await done('Пробить чек');

await go('#/trainer/nearest/hints');
await search('Название', 'терм'); await openRes('Термоглин 500');
await addLot('ТГ-2105', 1);
ok(await page.locator('.err').isVisible(), 'просроченную партию продать не дали');
await page.locator('[data-act=report]').click();
await addLot('ТГ-2207', 1); await page.locator('[data-act=scan]').click();
await page.locator('[data-act=pay][data-v=cash]').click();
const nT = await page.locator('#trainerHost').textContent();
ok(nT.includes('ошибок: 1') && nT.includes('просрочена'), 'Ближайший срок: завершён, попытка продать просрочку учтена как 1 ошибка');

await go('#/trainer/return/hints');
await page.locator('[data-act=tab][data-v=return]').click();
await page.locator('.result', { hasText: '№0007' }).click();
await page.fill('#rq0', '1'); await page.check('#retConf');
await page.locator('[data-act=retdo][data-v=card]').click(); await done('Возврат по чеку');

await go('#/trainer/resort/hints');
await page.locator('[data-act=tab][data-v=recv]').click();
await page.selectOption('#rv-r1', 'resort'); await page.selectOption('#rv-r2', 'resort'); await page.selectOption('#rv-r3', 'ok'); await page.selectOption('#rv-r4', 'defect');
await page.check('input[name=recvAct][value=hold]');
await page.locator('[data-act=recvdo]').click(); await done('Пересорт');

await go('#/trainer/rx/hints');
await search('Название', 'рец'); await openRes('Рецептин'); await addLot('РЦ-301', 1);
await page.locator('[data-act=choice][data-v=sell]').click();
ok(await page.locator('.err').isVisible(), 'продать рецептурный без рецепта не дали');
await page.locator('[data-act=choice][data-v=refuse]').click();
const rxT = await page.locator('#trainerHost h2').nth(1).textContent();
ok(rxT.includes('завершён'), 'рецептурный: сценарий завершён, ошибка учтена');

console.log('5. Тренажёр без подсказок — ошибки в разборе');
await go('#/trainer/sale/nohints');
ok(await page.locator('.steps').count() === 0, 'подсказок нет');
await search('Название', 'терм'); await openRes('Термоглин 500'); await addLot('ТГ-2301', 2);
await page.locator('[data-act=scan]').click(); await page.locator('[data-act=choice][data-v=retry]').click(); await page.locator('[data-act=scan]').click();
await search('Название', 'плас'); await openRes('Пластырь'); await addLot('ПЛ-12', 1);
await page.locator('[data-act=pay][data-v=cash]').click();
const errs = await page.locator('#trainerHost ol li').count();
ok(errs >= 2, 'разбор ошибок показан: ' + errs);
const tr = await page.evaluate(() => JSON.parse(localStorage.getItem('vika-aptek-v1')).trainer);
ok(tr.sale && tr.sale.hints === 100 && tr.sale.nohints < 100, 'результаты тренажёра сохранены');

console.log('6. Мой ассортимент + CSV');
await go('#/my');
await page.locator('#addBtn').click();
await page.fill('#f-name', 'Тестовое название'); await page.fill('#f-mnn', 'тестовое мнн'); await page.fill('#f-form', 'таблетки'); await page.fill('#f-dose', '100 мг'); await page.fill('#f-shelf', 'витрина 1');
await page.locator('#myForm button[type=submit]').click();
ok((await page.locator('#myList').textContent()).includes('Тестовое название'), 'позиция добавлена');
const [dl] = await Promise.all([page.waitForEvent('download'), page.locator('#csvOut').click()]);
const csvPath = join(shots, 'export.csv'); await dl.saveAs(csvPath);
const csv = readFileSync(csvPath, 'utf8');
ok(csv.includes('Тестовое название') && csv.includes('Название;МНН'), 'CSV экспортирован');
const csv2 = join(shots, 'import.csv');
writeFileSync(csv2, '﻿Название;МНН;Форма;Дозировка;Группа\r\n"Импорт ""кавычки""; тест";импмнн;сироп;100 мл;Горло\r\nТестовое название;тестовое мнн;таблетки;100 мг;\r\n');
await page.setInputFiles('#csvIn', csv2); await page.waitForTimeout(200);
ok((await page.locator('#myList').textContent()).includes('Импорт "кавычки"; тест'), 'CSV импортирован (кавычки, ; в ячейке), дубль пропущен');
ok(await page.evaluate(() => JSON.parse(localStorage.getItem('vika-aptek-v1')).assort.length) === 2, 'в ассортименте 2 позиции');
await page.fill('#mq', 'импмнн'); await page.waitForTimeout(50);
ok((await page.locator('#myList .card').count()) === 1, 'поиск работает');
await go('#/page/mnn');
ok((await page.locator('#mnnTable').textContent()).includes('импмнн'), 'таблица МНН собрана из ассортимента');

console.log('7. Карточки');
await go('#/cards');
await page.locator('#src').selectOption('mine'); await page.waitForTimeout(50);
await page.locator('#flip').click(); await page.locator('#yes').click();
await page.locator('#flip').click(); await page.locator('#no').click();
const cards = await page.evaluate(() => JSON.parse(localStorage.getItem('vika-aptek-v1')).cards);
ok(Object.values(cards).some(c => c.box === 2) && Object.values(cards).some(c => c.box === 1), 'Лейтнер: «знаю» → коробка 2, «не знаю» → 1');

console.log('8. Заметки, вопросы, план');
await go('#/notes'); await page.fill('#nt', 'Моя заметка'); await page.locator('#nf button').click();
await go('#/questions'); await page.fill('#qt', 'Мой вопрос'); await page.locator('#qf button').click();
await go('#/plan'); await page.locator('[data-plan="d1-0"]').check();

console.log('9. Резервная копия: экспорт → сброс → импорт');
await go('#/backup');
const [dl2] = await Promise.all([page.waitForEvent('download'), page.locator('#expBtn').click()]);
const bPath = join(shots, 'backup.json'); await dl2.saveAs(bPath);
const backup = JSON.parse(readFileSync(bPath, 'utf8'));
ok(backup.app === 'vika-aptek' && backup.data.notes.length === 1 && backup.data.questions.length === 1 && backup.data.assort.length === 2, 'копия содержит заметки, вопросы, ассортимент');
await page.locator('#resetBtn').click(); await page.waitForTimeout(100);
ok(await page.evaluate(() => JSON.parse(localStorage.getItem('vika-aptek-v1')).notes.length) === 0, 'сброс выполнен');
await go('#/backup');
await page.setInputFiles('#impFile', bPath); await page.waitForTimeout(200);
const restored = await page.evaluate(() => JSON.parse(localStorage.getItem('vika-aptek-v1')));
ok(restored.notes[0].text === 'Моя заметка' && restored.plan['d1-0'] === true && restored.lessons.what.done, 'данные восстановлены из копии');
await go('#/notes');
ok((await page.locator('#nl textarea').inputValue()) === 'Моя заметка', 'восстановленная заметка видна на странице');

console.log('10. Тёмная тема и скриншоты');
for (const [scheme, suffix] of [['light', 'light'], ['dark', 'dark']]) {
  await page.emulateMedia({ colorScheme: scheme, reducedMotion: 'reduce' });
  for (const h of ['#/', '#/lesson/sale', '#/group/allergy', '#/cards', '#/trainer/sale/hints']) {
    await go(h); await page.waitForTimeout(80);
    await page.screenshot({ path: join(shots, suffix + '-' + h.replace(/[#/]+/g, '_') + '.png') });
  }
}
await page.emulateMedia({ colorScheme: 'dark' }); await go('#/');
const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
ok(bg === 'rgb(18, 22, 20)', 'тёмная тема применяется: ' + bg);
await page.locator('#themeBtn').click(); // auto -> light
ok(await page.evaluate(() => document.documentElement.getAttribute('data-theme')) === 'light', 'переключатель темы работает');

console.log('11. Печать шпаргалки');
await go('#/cheat'); await page.emulateMedia({ media: 'print' });
ok(!(await page.locator('.bottomnav').isVisible()), 'в печати навигация скрыта');
await page.pdf({ path: join(shots, 'cheat.pdf') }).catch(() => {});
await page.emulateMedia({ media: 'screen' });

console.log('12. Без localStorage');
const ctx2 = await browser.newContext({ viewport: { width: 375, height: 700 } });
await ctx2.addInitScript(() => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } }); });
const p2 = await ctx2.newPage(); const e2 = []; p2.on('pageerror', e => e2.push(e.message));
await p2.goto(fileUrl); await p2.waitForTimeout(100);
ok(e2.length === 0 && (await p2.locator('text=Хранилище недоступно').count()) === 1, 'сайт работает и предупреждает, если хранилище заблокировано');

ok(external.length === 0, 'внешних запросов нет' + (external.length ? ': ' + external.join(', ') : ''));
ok(errors.length === 0, 'ошибок JS нет' + (errors.length ? ': ' + errors.join(' | ') : ''));
await browser.close();
console.log(fails ? '\nПРОВАЛЕНО: ' + fails : '\nВсё прошло.');
process.exit(fails ? 1 : 0);
