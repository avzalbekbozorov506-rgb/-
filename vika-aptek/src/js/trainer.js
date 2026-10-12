/* Тренажёр «Касса». Учебная модель на вымышленных товарах и условных ценах (у.е.).
   Не повторяет интерфейс какой-либо конкретной программы. */
(function () {
  'use strict';
  window.VA = window.VA || {};

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function dateIn(days) {
    var d = new Date(); d.setHours(12, 0, 0, 0); d.setDate(d.getDate() + days); return d;
  }
  function fmtDate(d) {
    return String(d.getDate()).padStart(2, '0') + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' + d.getFullYear();
  }
  function isExpired(lot) { return lot.exp < dateIn(0); }

  /* ---------- Вымышленный каталог ---------- */
  function catalog() {
    return [
      { id: 'p1', name: 'Термоглин 500 мг таблетки №20', mnn: 'условин', form: 'таблетки', dose: '500 мг', pack: '№20', maker: 'ООО «Учебфарм»', bc: '2000000000011', code: '10011', marked: true, rx: false, price: 120,
        lots: [{ lot: 'ТГ-2301', exp: dateIn(420), qty: 6 }, { lot: 'ТГ-2207', exp: dateIn(45), qty: 3 }, { lot: 'ТГ-2105', exp: dateIn(-4), qty: 1 }] },
      { id: 'p2', name: 'Термоглин 250 мг таблетки №20', mnn: 'условин', form: 'таблетки', dose: '250 мг', pack: '№20', maker: 'ООО «Учебфарм»', bc: '2000000000028', code: '10012', marked: true, rx: false, price: 90,
        lots: [{ lot: 'ТГ-1188', exp: dateIn(300), qty: 8 }] },
      { id: 'p3', name: 'Условин-Учеб 500 мг таблетки шипучие №10', mnn: 'условин', form: 'таблетки шипучие', dose: '500 мг', pack: '№10', maker: 'АО «Тренфарм»', bc: '2000000000035', code: '10013', marked: true, rx: false, price: 150,
        lots: [{ lot: 'УУ-0412', exp: dateIn(200), qty: 4 }, { lot: 'УУ-0377', exp: dateIn(90), qty: 2 }] },
      { id: 'p4', name: 'Термоглин Детский суспензия 100 мл', mnn: 'условин', form: 'суспензия для приёма внутрь', dose: '—', pack: '100 мл', maker: 'ООО «Учебфарм»', bc: '2000000000042', code: '10014', marked: true, rx: false, price: 170,
        lots: [{ lot: 'ТД-0090', exp: dateIn(260), qty: 5 }] },
      { id: 'p5', name: 'Носолин 0,1% спрей назальный 10 мл', mnn: 'учебназолин', form: 'спрей назальный', dose: '0,1%', pack: '10 мл', maker: 'ООО «Пример-Мед»', bc: '2000000000059', code: '20021', marked: true, rx: false, price: 110,
        lots: [{ lot: 'НС-551', exp: dateIn(500), qty: 7 }] },
      { id: 'p6', name: 'Носолин 0,05% спрей назальный детский 10 мл', mnn: 'учебназолин', form: 'спрей назальный', dose: '0,05%', pack: '10 мл', maker: 'ООО «Пример-Мед»', bc: '2000000000066', code: '20022', marked: true, rx: false, price: 105,
        lots: [{ lot: 'НС-560', exp: dateIn(480), qty: 5 }] },
      { id: 'p7', name: 'Горлодин таблетки для рассасывания №24', mnn: 'тренирол', form: 'таблетки для рассасывания', dose: '—', pack: '№24', maker: 'АО «Тренфарм»', bc: '2000000000073', code: '30031', marked: true, rx: false, price: 140,
        lots: [{ lot: 'ГД-771', exp: dateIn(380), qty: 9 }] },
      { id: 'p8', name: 'Пластырь бактерицидный учебный 1,9×7,2 см №10', mnn: '— (медицинское изделие)', form: 'пластырь', dose: '—', pack: '№10', maker: 'ООО «Пример-Мед»', bc: '2000000000080', code: '40041', marked: false, rx: false, price: 40,
        lots: [{ lot: 'ПЛ-12', exp: dateIn(900), qty: 20 }] },
      { id: 'p9', name: 'Рецептин 10 мг таблетки №30', mnn: 'примерол', form: 'таблетки', dose: '10 мг', pack: '№30', maker: 'АО «Тренфарм»', bc: '2000000000097', code: '50051', marked: true, rx: true, price: 300,
        lots: [{ lot: 'РЦ-301', exp: dateIn(600), qty: 4 }] }
    ];
  }

  function seedReceipts(P) {
    var g = P.filter(function (p) { return p.id === 'p7'; })[0];
    var pl = P.filter(function (p) { return p.id === 'p8'; })[0];
    return [
      { no: '0006', pay: 'cash', lines: [{ pid: 'p8', name: pl.name, lot: 'ПЛ-12', qty: 1, price: pl.price }] },
      { no: '0007', pay: 'card', lines: [{ pid: 'p7', name: g.name, lot: 'ГД-771', qty: 2, price: g.price }] }
    ];
  }

  /* ---------- Сценарии ---------- */
  function R(err, S, apply) {
    if (err && S.hints) return { err: err, block: true };
    if (apply) apply();
    return { err: err || null };
  }

  var SCEN = [
    {
      id: 'find', title: 'Найти товар',
      desc: 'Поиск по МНН, сверка формы и дозировки.',
      customer: '«Мне вот это лекарство, упаковку выбросила, помню только, что на ней было “условин 500 мг, шипучие”. Одну упаковку».',
      steps: [
        'Переключите режим поиска на «МНН».',
        'Введите первые буквы МНН — «усл» — и нажмите «Найти».',
        'Среди результатов откройте позицию, где форма — «таблетки шипучие», а дозировка — 500 мг.',
        'Выберите партию с ближайшим (не истёкшим) сроком, количество 1 — «Добавить в чек».',
        'Нажмите «Сканировать код маркировки» в строке чека.'
      ],
      step: function (S) { var f = S.f; return !f.found ? (S.mode === 'mnn' ? 1 : 0) : !f.opened ? 2 : !f.added ? 3 : !f.scanned ? 4 : 5; },
      on: function (ev, S) {
        if (ev.type === 'search') {
          if (ev.mode === 'mnn' && ev.ids.indexOf('p3') >= 0) S.f.found = true;
          return { err: null };
        }
        if (ev.type === 'open') {
          if (ev.pid === 'p3') { S.f.opened = true; S.f.found = true; return { err: null }; }
          if (ev.pid === 'p1' || ev.pid === 'p2' || ev.pid === 'p4') return { err: null, info: 'Это та же МНН, но другая форма или дозировка. Нужна форма «таблетки шипучие», 500 мг.' };
          return { err: null };
        }
        if (ev.type === 'add') {
          if (ev.pid !== 'p3') return R('Добавлена не та позиция. Сверьте 4 параметра: название, дозировку (500 мг), форму (шипучие), фасовку.', S);
          if (ev.qty !== 1) return R('Покупатель просил одну упаковку.', S, function () { S.f.added = true; });
          if (ev.lot !== 'УУ-0377') return R('Есть партия с более близким сроком (УУ-0377). Сначала продаём её.', S, function () { S.f.added = true; });
          S.f.added = true; return { err: null };
        }
        if (ev.type === 'scan' && ev.ok) {
          S.f.scanned = true; S.done = true; return { err: null };
        }
        return { err: null };
      }
    },
    {
      id: 'sale', title: 'Пробить чек',
      desc: 'Две позиции, маркировка, нечитаемый код, оплата картой.',
      customer: '«Термоглин 500 миллиграмм таблетки — две упаковки. И пластырь бактерицидный. Оплачу картой». (Штрихкод Термоглина на упаковке: 2000000000011.)',
      setup: function (S) { S.scanFailOnce = true; },
      steps: [
        'Найдите Термоглин 500 мг (можно по штрихкоду 2000000000011 в режиме «Штрихкод»).',
        'Откройте карточку, выберите партию с ближайшим не истёкшим сроком, количество 2, «Добавить в чек».',
        'Найдите пластырь (например, по названию «плас») и добавьте 1 упаковку.',
        'Отсканируйте коды маркировки у Термоглина — по одному на каждую упаковку. Если код не читается — выберите правильное действие.',
        'Проверьте чек и нажмите «Оплата: карта».'
      ],
      step: function (S) {
        var t = qtyOf(S, 'p1'), p = qtyOf(S, 'p8');
        if (!S.f.openedP1 && t === 0) return 0;
        if (t < 2) return 1;
        if (p < 1) return 2;
        if (scansMissing(S) > 0) return 3;
        return S.done ? 5 : 4;
      },
      on: function (ev, S) {
        if (ev.type === 'open' && ev.pid === 'p1') S.f.openedP1 = true;
        if (ev.type === 'add') {
          if (ev.pid !== 'p1' && ev.pid !== 'p8') return R('Этого товара покупатель не просил. Сверьте название, дозировку и форму.', S);
          if (ev.pid === 'p1' && ev.lot !== 'ТГ-2207') return R('Выбрана не та партия: сначала продаём партию с ближайшим не истёкшим сроком (ТГ-2207).', S);
          if (ev.pid === 'p1' && ev.qty + qtyOf(S, 'p1') > 2) return R('Покупатель просил 2 упаковки Термоглина.', S);
          if (ev.pid === 'p8' && ev.qty + qtyOf(S, 'p8') > 1) return R('Покупатель просил 1 пластырь.', S);
        }
        if (ev.type === 'choice' && ev.dialog === 'scanfail') {
          if (ev.value === 'other') return { err: 'Сканировать код с другой упаковки нельзя: в учёте окажется не та упаковка.' };
          if (ev.value === 'skip') return { err: 'Продавать маркированный товар в обход сканирования нельзя. Сначала повторите попытку, затем — к старшему по инструкции аптеки.' };
        }
        if (ev.type === 'payblocked') return { err: 'Попытка оплаты, пока отсканированы не все коды маркировки.' };
        if (ev.type === 'pay') {
          var e = null;
          if (qtyOf(S, 'p1') !== 2 || qtyOf(S, 'p8') !== 1 || S.cart.length > 2 && otherItems(S, ['p1', 'p8'])) e = 'Состав чека не совпадает с запросом: 2 × Термоглин 500 мг и 1 × пластырь.';
          else if (ev.method !== 'card') e = 'Покупатель хотел оплатить картой. Перед оплатой уточняйте способ оплаты.';
          return R(e, S, function () { S.done = true; });
        }
        return { err: null };
      }
    },
    {
      id: 'nearest', title: 'Ближайший срок годности',
      desc: 'Найти партию с ближайшим сроком, заметить просроченную.',
      customer: '«Термоглин 500 мг, одну упаковку, наличными».',
      steps: [
        'Найдите Термоглин 500 мг и откройте карточку.',
        'Посмотрите партии. Одна из них просрочена — нажмите у неё «Сообщить старшему».',
        'Выберите партию с ближайшим НЕ истёкшим сроком, количество 1 — «Добавить в чек».',
        'Отсканируйте код маркировки.',
        'Оплата: наличные.'
      ],
      step: function (S) {
        if (!S.f.opened) return 0;
        if (!S.f.reported) return 1;
        if (qtyOf(S, 'p1') < 1) return 2;
        if (scansMissing(S) > 0) return 3;
        return S.done ? 5 : 4;
      },
      on: function (ev, S) {
        if (ev.type === 'open' && ev.pid === 'p1') S.f.opened = true;
        if (ev.type === 'report') {
          if (ev.lot === 'ТГ-2105') { S.f.reported = true; return { err: null, ok: 'Верно: просроченную партию — в карантин, старшему сообщено (в учебной модели).' }; }
        }
        if (ev.type === 'add') {
          if (ev.pid !== 'p1') return R('Нужен Термоглин 500 мг таблетки.', S);
          if (ev.lot === 'ТГ-2105') return R('Эта партия просрочена! Её нельзя продавать — уберите из продажи и сообщите старшему.', S);
          if (ev.lot === 'ТГ-2301') return R('У партии ТГ-2301 срок дальше. Ближайший не истёкший — ТГ-2207.', S);
          if (ev.qty !== 1) return R('Нужна одна упаковка.', S);
        }
        if (ev.type === 'pay') {
          var e = null;
          if (!S.f.reported) e = 'Вы не сообщили о просроченной партии ТГ-2105. Найденная просрочка — всегда повод сразу сообщить старшему.';
          else if (ev.method !== 'cash') e = 'Покупатель платит наличными.';
          return R(e, S, function () { S.done = true; });
        }
        return { err: null };
      }
    },
    {
      id: 'return', title: 'Возврат по чеку',
      desc: 'Исправить ошибку кассира после закрытия чека — со старшим.',
      customer: 'Покупатель вернулся с чеком №0007: «Мне пробили 2 упаковки Горлодина, а дали одну». Старший проверил и разрешил оформить возврат 1 упаковки. Чек оплачивали картой.',
      steps: [
        'Перейдите на вкладку «Возврат».',
        'Выберите чек №0007.',
        'Укажите количество к возврату: Горлодин — 1.',
        'Отметьте «Старший подтвердил возврат».',
        'Верните деньги тем же способом, которым оплачивали (карта).'
      ],
      step: function (S) {
        if (S.tab !== 'return' && !S.f.selected) return 0;
        if (!S.f.selected) return 1;
        return S.done ? 5 : 2;
      },
      on: function (ev, S) {
        if (ev.type === 'retselect') {
          if (ev.no !== '0007') return R('Это не тот чек. Покупатель принёс чек №0007.', S);
          S.f.selected = true;
        }
        if (ev.type === 'retdo') {
          var e = null;
          if (ev.no !== '0007') e = 'Возврат оформлен не по тому чеку.';
          else if (!ev.confirmed) e = 'Возврат новичок оформляет только с подтверждения старшего (в модели — галочка).';
          else if (ev.qty !== 1) e = 'Вернуть нужно ровно 1 упаковку: вторую покупатель получил.';
          else if (ev.method !== 'card') e = 'Возврат делают тем же способом, что и оплату: чек оплачен картой. Уточняйте правила у старшего.';
          return R(e, S, function () { S.done = true; });
        }
        return { err: null };
      }
    },
    {
      id: 'resort', title: 'Пересорт при приёмке',
      desc: 'Сверить накладную и факт, назвать расхождения.',
      customer: 'Пришла поставка. Вас попросили помочь сверить товар с накладной и сказать, что не так. (Учебная ситуация: приёмку оформляет ответственный.)',
      steps: [
        'Перейдите на вкладку «Приёмка».',
        'Сравните накладную и факт по каждой строке. Обратите внимание на дозировки и состояние упаковок.',
        'Для каждой строки факта выберите статус.',
        'Выберите правильное действие с расхождениями и нажмите «Завершить сверку».'
      ],
      step: function (S) { return S.done ? 4 : (S.tab === 'recv' ? 2 : 0); },
      on: function (ev, S) {
        if (ev.type === 'recv') {
          var want = { r1: 'resort', r2: 'resort', r3: 'ok', r4: 'defect' };
          var names = { r1: 'Термоглин 250 мг: 8 вместо 10 — и при этом пришло 2 уп. 500 мг, которых нет в накладной. Это пересорт.', r2: 'Термоглин 500 мг (2 уп.) — не заказывался, пришёл вместо 250 мг. Это пересорт.', r3: 'Носолин 0,1%: 5 и 5 — совпадает.', r4: 'Горлодин: количество совпадает, но 1 упаковка повреждена — брак.' };
          var errs = [];
          Object.keys(want).forEach(function (k) { if (ev.answers[k] !== want[k]) errs.push(names[k]); });
          if (ev.action !== 'hold') errs.push(ev.action === 'fix' ? 'Самой править количество в программе нельзя: расхождения оформляет ответственный документами.' : 'Товар с расхождениями не выставляют в продажу до решения ответственного.');
          if (!ev.action) errs.push('Выберите действие с расхождениями.');
          if (errs.length && S.hints) return { err: errs.join(' '), block: true };
          S.done = true;
          return { err: errs.length ? errs : null };
        }
        return { err: null };
      }
    },
    {
      id: 'rx', title: 'Рецептурный без рецепта',
      desc: 'Программа подсказывает рецептурный статус. Как поступить.',
      customer: '«Рецептин 10 мг, пожалуйста. Рецепта нет, но я его давно пью».',
      steps: [
        'Найдите «Рецептин» по названию.',
        'Откройте карточку — обратите внимание на отметку «Рецептурный».',
        'Попробуйте добавить в чек — и выберите правильный вариант в окне вопроса.'
      ],
      step: function (S) { return S.done ? 3 : S.f.opened ? 2 : S.f.found ? 1 : 0; },
      on: function (ev, S) {
        if (ev.type === 'search' && ev.ids.indexOf('p9') >= 0) S.f.found = true;
        if (ev.type === 'open' && ev.pid === 'p9') { S.f.opened = true; S.f.found = true; }
        if (ev.type === 'choice' && ev.dialog === 'rx') {
          if (ev.value === 'refuse') { S.done = true; return { err: null }; }
          if (ev.value === 'sell') return R('Рецептурный препарат без рецепта отпускать нельзя, даже если покупатель «давно пьёт».', S, function () { S.done = true; });
          if (ev.value === 'analog') return R('Подбор замены рецептурному препарату — задача врача, а не фармацевта.', S, function () { S.done = true; });
        }
        return { err: null };
      }
    },
    {
      id: 'free', title: 'Свободная практика',
      desc: 'Без заданий: пробуйте любые операции.',
      customer: 'Свободный режим. Ищите, добавляйте, сканируйте, оплачивайте, оформляйте возвраты. Ошибки не считаются.',
      free: true,
      steps: ['Делайте что угодно — это песочница.'],
      step: function () { return 0; },
      on: function () { return { err: null }; }
    }
  ];

  function qtyOf(S, pid) { return S.cart.filter(function (l) { return l.pid === pid; }).reduce(function (a, l) { return a + l.qty; }, 0); }
  function otherItems(S, ids) { return S.cart.some(function (l) { return ids.indexOf(l.pid) < 0; }); }
  function prod(S, pid) { return S.P.filter(function (p) { return p.id === pid; })[0]; }
  function scansMissing(S) {
    return S.cart.reduce(function (a, l) { var p = prod(S, l.pid); return a + (p.marked ? Math.max(0, l.qty - l.scans) : 0); }, 0);
  }

  /* ---------- Состояние и действия ---------- */
  var S = null, host = null, onFinish = null;

  function start(el, id, mode, finishCb) {
    host = el; onFinish = finishCb;
    var sc = SCEN.filter(function (s) { return s.id === id; })[0] || SCEN[0];
    var P = catalog();
    S = { sc: sc, hints: mode !== 'nohints', P: P, mode: 'name', q: '', results: null, sel: null, cart: [], receipts: seedReceipts(P),
      nextNo: 8, f: {}, errors: [], msg: null, done: false, tab: 'sale', dialog: null, ret: { no: null, qty: {}, confirmed: false },
      recv: { answers: {}, action: '' }, lastReceipt: null, reported: {} };
    if (sc.setup) sc.setup(S);
    draw();
  }

  function emit(ev) {
    var r = S.sc.on(ev, S) || {};
    if (r.err) {
      var list = Array.isArray(r.err) ? r.err : [r.err];
      if (!S.sc.free) list.forEach(function (e) { S.errors.push(e); });
      S.msg = S.hints ? { kind: 'err', text: list.join(' ') } : null;
    } else if (r.ok) {
      S.msg = S.hints ? { kind: 'ok', text: r.ok } : null;
    } else if (r.info) {
      S.msg = S.hints ? { kind: 'hint', text: r.info } : null;
    } else {
      S.msg = null;
    }
    return !r.block;
  }

  var act = {
    tab: function (t) { S.tab = t; S.dialog = null; S.msg = null; draw(); },
    mode: function (m) { S.mode = m; draw(); },
    search: function (q) {
      S.q = q; var qq = q.trim().toLowerCase();
      var res = !qq ? [] : S.P.filter(function (p) {
        if (S.mode === 'name') return p.name.toLowerCase().indexOf(qq) >= 0;
        if (S.mode === 'mnn') return p.mnn.toLowerCase().indexOf(qq) === 0 || p.mnn.toLowerCase().indexOf(' ' + qq) >= 0;
        if (S.mode === 'bc') return p.bc === qq;
        if (S.mode === 'code') return p.code === qq;
        return false;
      });
      S.results = res.map(function (p) { return p.id; }); S.sel = null;
      emit({ type: 'search', mode: S.mode, q: q, ids: S.results.slice() });
      draw();
    },
    open: function (pid) { S.sel = pid; emit({ type: 'open', pid: pid }); draw(); },
    add: function (pid, lot, qty) {
      var p = prod(S, pid);
      qty = Math.max(1, parseInt(qty, 10) || 1);
      if (!lot) { S.msg = { kind: 'err', text: 'Выберите партию.' }; draw(); return; }
      if (p.rx) { S.dialog = { kind: 'rx', pid: pid, lot: lot, qty: qty }; S.msg = null; draw(); return; }
      if (emit({ type: 'add', pid: pid, lot: lot, qty: qty })) {
        var ex = S.cart.filter(function (l) { return l.pid === pid && l.lot === lot; })[0];
        if (ex) ex.qty += qty; else S.cart.push({ pid: pid, lot: lot, qty: qty, scans: 0, price: p.price });
      }
      draw();
    },
    qty: function (i, d) {
      var l = S.cart[i]; if (!l) return;
      var nq = l.qty + d;
      if (nq < 1) return;
      if (d > 0 && !emit({ type: 'add', pid: l.pid, lot: l.lot, qty: d })) { draw(); return; }
      l.qty = nq; if (l.scans > l.qty) l.scans = l.qty;
      draw();
    },
    remove: function (i) { var l = S.cart[i]; if (!l) return; emit({ type: 'remove', pid: l.pid }); S.cart.splice(i, 1); S.msg = S.msg || (S.hints ? { kind: 'hint', text: 'Позиция отменена (чек ещё не закрыт — так можно). В некоторых аптеках на это нужно подтверждение старшего.' } : null); draw(); },
    scan: function (i) {
      var l = S.cart[i]; if (!l) return;
      if (S.scanFailOnce) { S.scanFailOnce = false; S.dialog = { kind: 'scanfail', line: i }; S.msg = null; draw(); return; }
      if (l.scans < l.qty) { l.scans++; emit({ type: 'scan', ok: true, pid: l.pid }); }
      draw();
    },
    report: function (pid, lot) {
      S.reported[pid + lot] = true;
      emit({ type: 'report', pid: pid, lot: lot });
      draw();
    },
    choice: function (value) {
      var d = S.dialog; if (!d) return;
      var ok = emit({ type: 'choice', dialog: d.kind, value: value });
      if (d.kind === 'scanfail') {
        if (value === 'retry') { var l = S.cart[d.line]; if (l && l.scans < l.qty) { l.scans++; emit({ type: 'scan', ok: true, pid: l.pid }); } S.dialog = null; if (S.hints && !S.msg) S.msg = { kind: 'ok', text: 'Со второй попытки код считался. Если бы не считался — к старшему, по инструкции аптеки.' }; }
        else if (!S.hints || ok) { S.dialog = null; }
      } else if (d.kind === 'rx') {
        if (value === 'refuse') S.dialog = null;
        else if (!S.hints) S.dialog = null;
      }
      draw();
    },
    pay: function (method) {
      if (!S.cart.length) { S.msg = { kind: 'err', text: 'Чек пустой.' }; draw(); return; }
      if (scansMissing(S) > 0) { emit({ type: 'payblocked' }); S.msg = { kind: 'err', text: 'Касса (учебная): не все коды маркировки отсканированы. Оплата невозможна.' }; draw(); return; }
      if (!emit({ type: 'pay', method: method })) { draw(); return; }
      var lines = S.cart.map(function (l) { return { pid: l.pid, name: prod(S, l.pid).name, lot: l.lot, qty: l.qty, price: l.price }; });
      var no = String(S.nextNo++).padStart(4, '0');
      S.receipts.push({ no: no, pay: method, lines: lines });
      S.lastReceipt = { no: no, method: method, total: total(lines) };
      S.cart = []; S.sel = null; S.results = null; S.q = '';
      draw();
    },
    retSelect: function (no) {
      if (!emit({ type: 'retselect', no: no })) { draw(); return; }
      S.ret = { no: no, qty: {}, confirmed: false }; draw();
    },
    retDo: function (method) {
      var rc = S.receipts.filter(function (r) { return r.no === S.ret.no; })[0]; if (!rc) return;
      var q = 0; Object.keys(S.ret.qty).forEach(function (k) { q += S.ret.qty[k] || 0; });
      if (q === 0) { S.msg = { kind: 'err', text: 'Укажите количество к возврату.' }; draw(); return; }
      if (!emit({ type: 'retdo', no: rc.no, qty: q, method: method, confirmed: S.ret.confirmed })) { draw(); return; }
      S.lastReceipt = { no: 'В-' + rc.no, method: method, total: -rc.lines.reduce(function (a, l, i) { return a + (S.ret.qty[i] || 0) * l.price; }, 0), ret: true };
      S.ret = { no: null, qty: {}, confirmed: false };
      draw();
    },
    recvDo: function () {
      emit({ type: 'recv', answers: S.recv.answers, action: S.recv.action });
      draw();
    }
  };

  function total(lines) { return lines.reduce(function (a, l) { return a + l.qty * l.price; }, 0); }

  /* ---------- Отрисовка ---------- */
  function draw() {
    if (!host) return;
    var sc = S.sc, h = '';
    h += '<div class="card task"><div class="row"><h2 style="margin:0">' + esc(sc.title) + '</h2><span class="spacer"></span>' +
      '<span class="badge ' + (S.hints ? 'acc' : 'warn') + '">' + (sc.free ? 'песочница' : S.hints ? 'с подсказками' : 'без подсказок') + '</span></div>' +
      '<p><b>Ситуация:</b> ' + esc(sc.customer) + '</p>';
    if (S.hints && !sc.free) {
      var si = sc.step(S);
      h += '<ol class="steps">' + sc.steps.map(function (t, i) {
        return '<li style="' + (i < si ? 'opacity:.55;text-decoration:line-through' : i === si ? 'font-weight:700' : '') + '">' + esc(t) + '</li>';
      }).join('') + '</ol>';
    } else if (!sc.free) {
      h += '<p class="muted">Подсказок нет. Ошибки покажем в разборе после завершения.</p>';
    }
    if (S.msg) h += '<div class="' + (S.msg.kind === 'err' ? 'err' : S.msg.kind === 'ok' ? 'okmsg' : 'hint') + '" role="status">' + esc(S.msg.text) + '</div>';
    h += '</div>';

    if (S.done && !sc.free) {
      h += summary();
      host.innerHTML = h; bind(); return;
    }

    h += '<div class="pos"><div class="pos-head"><span>Учебная касса · вымышленные товары · цены в у.е.</span><span>' + fmtDate(dateIn(0)) + '</span></div><div class="pos-body">';
    h += '<div class="seg" role="tablist">' +
      tabBtn('sale', 'Продажа') + tabBtn('return', 'Возврат') + tabBtn('recv', 'Приёмка') + '</div>';
    if (S.tab === 'sale') h += drawSale();
    else if (S.tab === 'return') h += drawReturn();
    else h += drawRecv();
    h += '</div></div>';
    h += '<div class="row" style="margin-top:12px"><a class="btn small" href="#/trainer">← Все сценарии</a><span class="spacer"></span>' +
      '<button class="btn small ghost" data-act="restart">Начать заново</button></div>';
    host.innerHTML = h; bind();
  }

  function tabBtn(id, t) { return '<button class="btn small' + (S.tab === id ? ' on' : '') + '" data-act="tab" data-v="' + id + '" role="tab" aria-selected="' + (S.tab === id) + '">' + t + '</button>'; }

  function drawSale() {
    var h = '';
    if (S.dialog) h += drawDialog();
    if (S.lastReceipt) {
      h += '<div class="okmsg">' + (S.lastReceipt.ret ? 'Возврат оформлен' : 'Чек №' + S.lastReceipt.no + ' закрыт') + ': ' + (S.lastReceipt.method === 'card' ? 'карта' : 'наличные') + ', ' + S.lastReceipt.total + ' у.е.</div>';
    }
    h += '<label>Режим поиска</label><div class="seg">' +
      [['name', 'Название'], ['mnn', 'МНН'], ['bc', 'Штрихкод'], ['code', 'Код']].map(function (m) {
        return '<button class="btn small' + (S.mode === m[0] ? ' on' : '') + '" data-act="mode" data-v="' + m[0] + '">' + m[1] + '</button>';
      }).join('') + '</div>';
    h += '<form class="row" data-form="search" style="margin-top:8px"><input type="search" name="q" value="' + esc(S.q) + '" placeholder="' +
      (S.mode === 'bc' ? '13 цифр штрихкода' : S.mode === 'code' ? 'код товара' : '3–4 первые буквы') + '" aria-label="Поиск" style="flex:1;min-width:150px" autocomplete="off">' +
      '<button class="btn primary" type="submit">Найти</button></form>';
    if (S.results) {
      if (!S.results.length) h += '<p class="muted">Ничего не найдено. Проверьте режим поиска и написание.</p>';
      S.results.forEach(function (pid) {
        var p = prod(S, pid);
        var free = p.lots.filter(function (l) { return !isExpired(l); }).reduce(function (a, l) { return a + l.qty; }, 0);
        h += '<button class="result' + (S.sel === pid ? ' sel' : '') + '" data-act="open" data-v="' + pid + '"><b>' + esc(p.name) + '</b>' +
          (p.rx ? ' <span class="badge danger">Рецептурный</span>' : '') + (p.marked ? ' <span class="badge">маркировка</span>' : '') +
          '<br><small>МНН: ' + esc(p.mnn) + ' · ' + esc(p.maker) + ' · остаток ' + free + ' · ' + p.price + ' у.е.</small></button>';
      });
    }
    if (S.sel) {
      var p = prod(S, S.sel);
      h += '<div class="card" style="margin-top:10px"><h3>' + esc(p.name) + '</h3>' +
        '<div class="table-wrap"><table style="min-width:0"><tr><th>МНН</th><td>' + esc(p.mnn) + '</td></tr><tr><th>Форма</th><td>' + esc(p.form) + '</td></tr>' +
        '<tr><th>Дозировка</th><td>' + esc(p.dose) + '</td></tr><tr><th>Фасовка</th><td>' + esc(p.pack) + '</td></tr><tr><th>Производитель</th><td>' + esc(p.maker) + '</td></tr>' +
        '<tr><th>Штрихкод / код</th><td>' + p.bc + ' / ' + p.code + '</td></tr><tr><th>Отпуск</th><td>' + (p.rx ? '<b style="color:var(--danger)">по рецепту</b>' : 'без рецепта') + '</td></tr></table></div>' +
        '<b>Партии</b>';
      p.lots.forEach(function (l) {
        var exp = isExpired(l);
        h += '<label class="lot' + (exp ? ' expired' : '') + '" style="font-weight:400;margin:0"><input type="radio" name="lot" value="' + l.lot + '"> ' +
          '<span style="flex:1">' + l.lot + ' · годен до ' + fmtDate(l.exp) + ' · ' + l.qty + ' шт.' + (exp ? ' · <b>СРОК ИСТЁК</b>' : '') + '</span>' +
          (exp ? (S.reported[p.id + l.lot] ? '<span class="badge ok">сообщено</span>' : '<button type="button" class="btn small danger" data-act="report" data-v="' + l.lot + '">Сообщить старшему</button>') : '') +
          '</label>';
      });
      h += '<div class="row" style="margin-top:10px"><label for="qtyIn" style="margin:0">Кол-во</label><input id="qtyIn" type="number" min="1" value="1" inputmode="numeric" style="width:90px">' +
        '<button class="btn primary" data-act="add">Добавить в чек</button></div></div>';
    }
    // чек
    h += '<h3>Чек</h3>';
    if (!S.cart.length) h += '<p class="muted">Пусто.</p>';
    S.cart.forEach(function (l, i) {
      var p = prod(S, l.pid);
      h += '<div class="line"><div><b>' + esc(p.name) + '</b><br><small>партия ' + l.lot + ' · ' + l.price + ' у.е.</small>' +
        (p.marked ? '<br><small>Коды маркировки: <b>' + l.scans + ' / ' + l.qty + '</b></small>' : '') + '</div>' +
        '<div style="text-align:right"><div class="row end"><button class="btn small icon" data-act="qty" data-i="' + i + '" data-v="-1" aria-label="Меньше">−</button><b>' + l.qty + '</b>' +
        '<button class="btn small icon" data-act="qty" data-i="' + i + '" data-v="1" aria-label="Больше">+</button></div></div>' +
        '<div class="row" style="grid-column:1/-1">' + (p.marked && l.scans < l.qty ? '<button class="btn small primary" data-act="scan" data-i="' + i + '">Сканировать код маркировки</button>' : '') +
        '<button class="btn small danger" data-act="remove" data-i="' + i + '">Отменить позицию</button></div></div>';
    });
    h += '<div class="total">Итого: ' + total(S.cart) + ' у.е.</div>';
    h += '<div class="row"><button class="btn primary" style="flex:1" data-act="pay" data-v="cash"' + (S.cart.length ? '' : ' disabled') + '>Оплата: наличные</button>' +
      '<button class="btn primary" style="flex:1" data-act="pay" data-v="card"' + (S.cart.length ? '' : ' disabled') + '>Оплата: карта</button></div>';
    return h;
  }

  function drawDialog() {
    var d = S.dialog, h = '<div class="card" role="dialog" aria-label="Вопрос" style="border:2px solid var(--warn)">';
    if (d.kind === 'scanfail') {
      h += '<h3>Код маркировки не считывается</h3><p>Сканер не прочитал код с упаковки. Что делаете?</p><div class="opts">' +
        '<button class="opt" data-act="choice" data-v="retry">Протереть окно сканера, развернуть упаковку, убрать блики и попробовать ещё раз; если не выйдет — позвать старшего</button>' +
        '<button class="opt" data-act="choice" data-v="other">Отсканировать код с другой такой же упаковки с полки</button>' +
        '<button class="opt" data-act="choice" data-v="skip">Продать без сканирования, чтобы не задерживать очередь</button></div>';
    } else if (d.kind === 'rx') {
      h += '<h3>Препарат отпускается по рецепту</h3><p>Учебная касса спрашивает: есть ли рецепт? Покупатель говорит, что рецепта нет.</p><div class="opts">' +
        '<button class="opt" data-act="choice" data-v="refuse">Вежливо объяснить, что без рецепта отпустить нельзя, и предложить обратиться к врачу</button>' +
        '<button class="opt" data-act="choice" data-v="sell">Продать, раз покупатель давно его принимает</button>' +
        '<button class="opt" data-act="choice" data-v="analog">Предложить «похожий» препарат вместо него</button></div>';
    }
    return h + '</div>';
  }

  function drawReturn() {
    var h = '';
    if (S.lastReceipt && S.lastReceipt.ret) h += '<div class="okmsg">Возврат оформлен: ' + (S.lastReceipt.method === 'card' ? 'на карту' : 'наличными') + ', ' + S.lastReceipt.total + ' у.е.</div>';
    h += '<p class="muted">Учебная модель. В реальной аптеке возврат оформляется по инструкции и, как правило, со старшим.</p>';
    if (!S.ret.no) {
      h += '<b>Закрытые чеки смены</b>';
      S.receipts.slice().reverse().forEach(function (r) {
        h += '<button class="result" data-act="retsel" data-v="' + r.no + '"><b>Чек №' + r.no + '</b> · ' + (r.pay === 'card' ? 'карта' : 'наличные') + ' · ' + total(r.lines) + ' у.е.<br><small>' +
          r.lines.map(function (l) { return esc(l.name) + ' × ' + l.qty; }).join('; ') + '</small></button>';
      });
      return h;
    }
    var rc = S.receipts.filter(function (r) { return r.no === S.ret.no; })[0];
    h += '<h3>Возврат по чеку №' + rc.no + '</h3><p>Оплата: <b>' + (rc.pay === 'card' ? 'карта' : 'наличные') + '</b></p>';
    rc.lines.forEach(function (l, i) {
      h += '<div class="line"><div><b>' + esc(l.name) + '</b><br><small>в чеке: ' + l.qty + ' шт.</small></div><div><label for="rq' + i + '" class="sr-only">Вернуть</label>' +
        '<input id="rq' + i + '" data-retq="' + i + '" type="number" min="0" max="' + l.qty + '" value="' + (S.ret.qty[i] || 0) + '" style="width:80px" inputmode="numeric"></div></div>';
    });
    h += '<label class="check-row"><input type="checkbox" id="retConf"' + (S.ret.confirmed ? ' checked' : '') + '> Старший подтвердил возврат</label>';
    h += '<div class="row"><button class="btn primary" style="flex:1" data-act="retdo" data-v="cash">Вернуть наличными</button><button class="btn primary" style="flex:1" data-act="retdo" data-v="card">Вернуть на карту</button></div>' +
      '<button class="btn small ghost" data-act="retback" style="margin-top:8px">← К списку чеков</button>';
    return h;
  }

  var RECV = [
    { id: 'r1', inv: 'Термоглин 250 мг таблетки №20 — 10 уп.', fact: 'Термоглин 250 мг таблетки №20 — 8 уп.' },
    { id: 'r2', inv: '— (нет в накладной)', fact: 'Термоглин 500 мг таблетки №20 — 2 уп.' },
    { id: 'r3', inv: 'Носолин 0,1% спрей 10 мл — 5 уп.', fact: 'Носолин 0,1% спрей 10 мл — 5 уп.' },
    { id: 'r4', inv: 'Горлодин таблетки №24 — 6 уп.', fact: 'Горлодин таблетки №24 — 6 уп., из них 1 с порванной упаковкой' }
  ];
  function drawRecv() {
    var h = '<p class="muted">Учебная сверка. Реальную приёмку оформляет ответственный по инструкции аптеки.</p>';
    var opts = [['', '— выберите —'], ['ok', 'Совпадает'], ['short', 'Недостача'], ['excess', 'Излишек'], ['resort', 'Пересорт'], ['defect', 'Брак']];
    RECV.forEach(function (r) {
      h += '<div class="card" style="margin:8px 0;padding:10px 12px"><small class="muted">Накладная:</small> ' + esc(r.inv) + '<br><small class="muted">Факт:</small> <b>' + esc(r.fact) + '</b>' +
        '<label for="rv-' + r.id + '">Статус</label><select id="rv-' + r.id + '" data-recv="' + r.id + '">' +
        opts.map(function (o) { return '<option value="' + o[0] + '"' + (S.recv.answers[r.id] === o[0] ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('') + '</select></div>';
    });
    h += '<b>Что делать с расхождениями?</b><div class="opts">' +
      [['hold', 'Отложить спорный товар, не выставлять в продажу, сообщить ответственному для оформления акта'], ['fix', 'Самой исправить количество в программе, чтобы сошлось'], ['sell', 'Выставить всё в продажу, разберёмся потом']].map(function (o) {
        return '<label class="check-row" style="border:1px solid var(--line);border-radius:10px;padding:10px"><input type="radio" name="recvAct" value="' + o[0] + '"' + (S.recv.action === o[0] ? ' checked' : '') + '> ' + o[1] + '</label>';
      }).join('') + '</div><button class="btn primary block" data-act="recvdo">Завершить сверку</button>';
    return h;
  }

  function summary() {
    var n = S.errors.length, score = Math.max(0, 100 - n * 25);
    var h = '<div class="card"><h2>' + (n === 0 ? 'Готово без ошибок!' : 'Сценарий завершён') + '</h2>' +
      '<p>Результат: <b>' + score + ' / 100</b> · ошибок: ' + n + '</p>' +
      '<div class="progress" aria-hidden="true"><i style="transform:scaleX(' + (score / 100) + ')"></i></div>';
    if (n) {
      h += '<h3>Разбор ошибок</h3><ol>' + S.errors.map(function (e) { return '<li>' + esc(e) + '</li>'; }).join('') + '</ol>';
    } else {
      h += '<p>Вы сделали всё по порядку. ' + (S.hints ? 'Попробуйте теперь режим «без подсказок».' : 'Отличная самопроверка!') + '</p>';
    }
    h += '<div class="row"><button class="btn primary" data-act="restart">Ещё раз</button>' +
      (S.hints ? '<a class="btn" href="#/trainer/' + S.sc.id + '/nohints">Без подсказок</a>' : '<a class="btn" href="#/trainer/' + S.sc.id + '/hints">С подсказками</a>') +
      '<a class="btn ghost" href="#/trainer">Все сценарии</a></div></div>';
    if (onFinish) { var cb = onFinish; onFinish = null; cb(S.sc.id, S.hints ? 'hints' : 'nohints', score); }
    return h;
  }

  function bind() {
    host.querySelectorAll('[data-act]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        var a = b.getAttribute('data-act'), v = b.getAttribute('data-v'), i = parseInt(b.getAttribute('data-i'), 10);
        if (a === 'tab') act.tab(v);
        else if (a === 'mode') act.mode(v);
        else if (a === 'open') act.open(v);
        else if (a === 'add') {
          var r = host.querySelector('input[name=lot]:checked');
          act.add(S.sel, r ? r.value : null, host.querySelector('#qtyIn').value);
        }
        else if (a === 'report') { e.preventDefault(); act.report(S.sel, v); }
        else if (a === 'qty') act.qty(i, parseInt(v, 10));
        else if (a === 'remove') act.remove(i);
        else if (a === 'scan') act.scan(i);
        else if (a === 'choice') act.choice(v);
        else if (a === 'pay') act.pay(v);
        else if (a === 'retsel') act.retSelect(v);
        else if (a === 'retback') { S.ret = { no: null, qty: {}, confirmed: false }; draw(); }
        else if (a === 'retdo') act.retDo(v);
        else if (a === 'recvdo') act.recvDo();
        else if (a === 'restart') start(host, S.sc.id, S.hints ? 'hints' : 'nohints', onFinishSaved);
      });
    });
    var f = host.querySelector('[data-form=search]');
    if (f) f.addEventListener('submit', function (e) { e.preventDefault(); act.search(f.q.value); });
    host.querySelectorAll('[data-retq]').forEach(function (inp) {
      inp.addEventListener('input', function () {
        var i = inp.getAttribute('data-retq'), max = parseInt(inp.max, 10);
        S.ret.qty[i] = Math.min(max, Math.max(0, parseInt(inp.value, 10) || 0));
      });
    });
    var rc = host.querySelector('#retConf');
    if (rc) rc.addEventListener('change', function () { S.ret.confirmed = rc.checked; });
    host.querySelectorAll('[data-recv]').forEach(function (sel) {
      sel.addEventListener('change', function () { S.recv.answers[sel.getAttribute('data-recv')] = sel.value; });
    });
    host.querySelectorAll('input[name=recvAct]').forEach(function (r) {
      r.addEventListener('change', function () { S.recv.action = r.value; });
    });
  }

  var onFinishSaved = null;
  window.VA.trainer = {
    scenarios: SCEN.map(function (s) { return { id: s.id, title: s.title, desc: s.desc, free: !!s.free }; }),
    start: function (el, id, mode, cb) { onFinishSaved = cb; start(el, id, mode, cb); }
  };
})();
