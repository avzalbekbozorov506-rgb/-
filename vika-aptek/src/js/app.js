/* Приложение: роутер и экраны. */
(function () {
  'use strict';
  var VA = window.VA, store = VA.store, D = function () { return store.data; };
  var app = document.getElementById('app');

  /* ---------- Утилиты ---------- */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function $(sel, root) { return (root || app).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || app).querySelectorAll(sel)); }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function pct(a, b) { return b ? Math.round(a / b * 100) : 0; }
  function bar(a, b) { return '<div class="progress" aria-label="' + pct(a, b) + '%"><i style="transform:scaleX(' + (b ? a / b : 0) + ')"></i></div>'; }
  function save() { if (!store.save()) toast('Не удалось сохранить: хранилище браузера недоступно. Сделайте резервную копию.'); }
  var toastTimer;
  function toast(t) {
    var old = document.querySelector('.toast'); if (old) old.remove();
    var el = document.createElement('div'); el.className = 'toast'; el.setAttribute('role', 'status'); el.textContent = t;
    document.body.appendChild(el); clearTimeout(toastTimer); toastTimer = setTimeout(function () { el.remove(); }, 2600);
  }
  function notices() {
    return '<div class="notices">' +
      '<div class="notice model"><b>Учебная модель.</b>В вашей аптеке окна и кнопки могут отличаться. Сверяйтесь с инструкцией работодателя и наставником.</div>' +
      '<div class="notice med"><b>Напоминание.</b>Фармацевт не ставит диагнозов и не назначает лечение. При тревожных симптомах, у беременных, детей и пожилых — направляйте к врачу. Дозировки и применение берутся из инструкции к препарату и назначения врача.</div>' +
      '</div>';
  }
  function page(title, body, opts) {
    opts = opts || {};
    var back = opts.back ? '<a class="btn small ghost no-print" href="' + opts.back + '">← Назад</a>' : '';
    return '<div class="view">' + back + '<h1>' + title + '</h1>' + notices() + body + '</div>';
  }
  function lessonById(id) { return VA.lessons.filter(function (l) { return l.id === id; })[0]; }
  function groupById(id) { return VA.groups.filter(function (g) { return g.id === id; })[0]; }

  /* ---------- Вопросы ---------- */
  function allQuestions() {
    var out = [];
    VA.lessons.forEach(function (l) { l.quiz.forEach(function (q, i) { out.push(Object.assign({ id: 'L:' + l.id + ':' + i, src: l.title }, q)); }); });
    VA.groups.forEach(function (g) { g.quiz.forEach(function (q, i) { out.push(Object.assign({ id: 'G:' + g.id + ':' + i, src: g.title }, q)); }); });
    return out;
  }
  function withIds(list, prefix, src) { return list.map(function (q, i) { return Object.assign({ id: prefix + i, src: src }, q); }); }

  /* Тест: по одному вопросу, объяснение после ответа. */
  function quiz(el, questions, onDone) {
    var idx = 0, right = 0, wrongList = [];
    var qs = questions.map(function (q) {
      var order = shuffle(q.a.map(function (_, i) { return i; }));
      return Object.assign({}, q, { order: order });
    });
    function show() {
      if (idx >= qs.length) return finish();
      var q = qs[idx];
      el.innerHTML = '<div class="card"><div class="row"><small class="muted">Вопрос ' + (idx + 1) + ' из ' + qs.length + (q.src ? ' · ' + esc(q.src) : '') + '</small></div>' +
        bar(idx, qs.length) + '<p class="q" style="margin-top:10px">' + esc(q.q) + '</p><div class="opts">' +
        q.order.map(function (i) { return '<button class="opt" data-i="' + i + '">' + esc(q.a[i]) + '</button>'; }).join('') +
        '</div><div class="fb"></div></div>';
      $$('.opt', el).forEach(function (b) {
        b.addEventListener('click', function () {
          var i = parseInt(b.getAttribute('data-i'), 10), ok = i === q.c;
          $$('.opt', el).forEach(function (o) {
            o.disabled = true;
            var oi = parseInt(o.getAttribute('data-i'), 10);
            if (oi === q.c) o.classList.add('right'); else if (oi === i) o.classList.add('wrong');
          });
          if (ok) { right++; delete D().wrong[q.id]; } else { D().wrong[q.id] = true; wrongList.push(q); }
          save();
          $('.fb', el).innerHTML = '<div class="explain"><b>' + (ok ? 'Верно.' : 'Не совсем.') + '</b> ' + esc(q.e) + '</div>' +
            '<div class="row end" style="margin-top:10px"><button class="btn primary next">' + (idx + 1 < qs.length ? 'Дальше' : 'Результат') + '</button></div>';
          var nb = $('.next', el); nb.addEventListener('click', function () { idx++; show(); }); nb.focus();
        });
      });
    }
    function finish() {
      el.innerHTML = '<div class="card"><h2>Результат: ' + right + ' из ' + qs.length + '</h2>' + bar(right, qs.length) +
        (wrongList.length ? '<h3>Повторите</h3><ul>' + wrongList.map(function (q) { return '<li><b>' + esc(q.q) + '</b><br>Ответ: ' + esc(q.a[q.c]) + '. <span class="muted">' + esc(q.e) + '</span></li>'; }).join('') + '</ul>' : '<p>Все ответы верные!</p>') +
        '<div class="row"><button class="btn primary again">Пройти ещё раз</button></div></div>';
      $('.again', el).addEventListener('click', function () { idx = 0; right = 0; wrongList = []; qs = shuffle(qs); show(); });
      if (onDone) onDone(right, qs.length);
    }
    show();
  }

  /* ---------- Экраны ---------- */
  var routes = {};

  routes[''] = function () {
    var d = D();
    var lessonsDone = VA.lessons.filter(function (l) { return d.lessons[l.id] && d.lessons[l.id].done; }).length;
    var groupsDone = VA.groups.filter(function (g) { return d.groups[g.id]; }).length;
    var trDone = VA.trainer.scenarios.filter(function (s) { return !s.free && d.trainer[s.id]; }).length;
    var trTotal = VA.trainer.scenarios.filter(function (s) { return !s.free; }).length;
    var planTotal = 0, planDone = 0, curDay = null;
    VA.plan.forEach(function (day) {
      day.tasks.forEach(function (t, i) { planTotal++; if (d.plan['d' + day.day + '-' + i]) planDone++; });
      if (!curDay && day.tasks.some(function (t, i) { return !d.plan['d' + day.day + '-' + i]; })) curDay = day;
    });
    var due = cardDeck().filter(isDue).length;
    var todayCount = d.cardLog[store.today()] || 0;
    var h = '<p>Привет, Вика! Здесь — короткие уроки, тренажёр кассы и карточки, чтобы за 2–3 недели уверенно работать за кассой и в зале. По 20–30 минут в день достаточно.</p>';
    if (!store.isAvailable()) h += '<div class="box important"><b>Хранилище недоступно</b>Браузер не даёт сохранять прогресс (например, приватный режим). Всё работает, но после закрытия вкладки прогресс пропадёт.</div>';
    if (curDay) {
      h += '<div class="card"><div class="row"><h2 style="margin:0">День ' + curDay.day + ': ' + esc(curDay.theme) + '</h2><span class="spacer"></span><a class="btn small" href="#/plan">План</a></div><ul style="list-style:none;padding:0">' +
        curDay.tasks.map(function (t, i) {
          var k = 'd' + curDay.day + '-' + i;
          return '<li><label class="check-row"><input type="checkbox" data-plan="' + k + '"' + (d.plan[k] ? ' checked' : '') + '> <span><a href="' + t.link + '">' + esc(t.t) + '</a></span></label></li>';
        }).join('') + '</ul></div>';
    } else {
      h += '<div class="card"><h2>План на 14 дней выполнен 🎉</h2><p>Продолжайте карточки и пополняйте «Мой ассортимент».</p></div>';
    }
    h += '<div class="card"><h2>Прогресс</h2>' +
      '<p>Уроки 1С: ' + lessonsDone + ' из ' + VA.lessons.length + '</p>' + bar(lessonsDone, VA.lessons.length) +
      '<p>Тесты по группам ассортимента: ' + groupsDone + ' из ' + VA.groups.length + '</p>' + bar(groupsDone, VA.groups.length) +
      '<p>Сценарии тренажёра: ' + trDone + ' из ' + trTotal + '</p>' + bar(trDone, trTotal) +
      '<p>План: ' + planDone + ' из ' + planTotal + '</p>' + bar(planDone, planTotal) +
      '<p>Карточки сегодня: ' + todayCount + ' из ' + d.cardGoal + ' · к повтору: ' + due + '</p>' + bar(Math.min(todayCount, d.cardGoal), d.cardGoal) + '</div>';
    h += '<div class="grid two">' +
      tile('#/trainer', 'Тренажёр «Касса»', 'Найти товар, пробить чек, возврат, сроки, пересорт') +
      tile('#/cards', 'Карточки', 'Препарат → МНН, группа, форма') +
      tile('#/my', 'Мой ассортимент', 'Реальные товары вашей аптеки: ' + d.assort.length) +
      tile('#/cheat', 'Шпаргалка на смену', 'Можно распечатать') + '</div>';
    return page('Аптека: старт', h);
  };
  function tile(href, t, d, badge) { return '<a class="tile" href="' + href + '">' + (badge || '') + '<span class="t">' + t + '</span><span class="d">' + d + '</span></a>'; }

  routes['1c'] = function () {
    var d = D();
    var h = '<p>Общее понимание учётной программы на базе 1С без привязки к конкретному интерфейсу. Каждый урок: короткая теория, схема, 5–7 вопросов.</p><div class="grid">';
    VA.lessons.forEach(function (l, i) {
      var st = d.lessons[l.id];
      var badge = st && st.done ? '<span class="badge ok badge">' + st.best + '/' + st.total + '</span>' : st ? '<span class="badge warn">' + st.best + '/' + st.total + '</span>' : '<span class="badge">' + l.min + ' мин</span>';
      h += tile('#/lesson/' + l.id, (i + 1) + '. ' + esc(l.title), esc(l.short), badge);
    });
    h += '</div><div class="card"><h2>Тренажёр «Касса»</h2><p>Интерактивная учебная касса на вымышленных товарах.</p><a class="btn primary" href="#/trainer">Открыть тренажёр</a></div>';
    return page('Модуль 1. 1С для новичка', h);
  };

  routes['lesson'] = function (id) {
    var l = lessonById(id); if (!l) return notFound();
    var i = VA.lessons.indexOf(l), next = VA.lessons[i + 1];
    var h = '<div class="card"><div class="schema">' + l.svg + '</div>' + l.body + '</div>' +
      '<h2>Проверьте себя</h2><div id="quiz"></div>' +
      '<div class="row">' + (next ? '<a class="btn" href="#/lesson/' + next.id + '">Следующий урок →</a>' : '<a class="btn" href="#/trainer">К тренажёру →</a>') + '</div>';
    setTimeout(function () {
      quiz($('#quiz'), withIds(l.quiz, 'L:' + l.id + ':', ''), function (r, t) {
        var st = D().lessons[l.id] || { best: 0, total: t };
        st.best = Math.max(st.best, r); st.total = t; if (r / t >= 0.7) st.done = true;
        D().lessons[l.id] = st; save();
        if (r / t >= 0.7) toast('Урок засчитан!'); else toast('Для зачёта нужно 70% верных ответов.');
      });
    });
    return page(esc(l.title), h, { back: '#/1c' });
  };

  routes['assort'] = function () {
    var d = D();
    var h = '<p>Общий каталог даёт основу, но не заменяет реальный ассортимент вашей аптеки. Главный способ учить — раздел «Мой ассортимент» и карточки по нему.</p>';
    h += '<div class="grid two">' + tile('#/my', 'Мой ассортимент', 'Заполняете сами: ' + d.assort.length + ' позиций') +
      tile('#/test/mixed', 'Смешанный тест', 'Случайные вопросы по всем темам') +
      tile('#/test/wrong', 'Повтор ошибок', 'Вопросов с ошибками: ' + Object.keys(d.wrong).length) +
      tile('#/cards', 'Карточки', 'Интервальные повторения') + '</div>';
    h += '<h2>Основы</h2><div class="grid">';
    VA.assortPages.forEach(function (p) { h += tile('#/page/' + p.id, esc(p.title), ''); });
    h += '</div><h2>Группы по назначению</h2><div class="grid two">';
    VA.groups.forEach(function (g) {
      var st = d.groups[g.id];
      h += tile('#/group/' + g.id, esc(g.title), g.items.length + ' позиций-примеров', st ? '<span class="badge ' + (st.best / st.total >= 0.7 ? 'ok' : 'warn') + '">' + st.best + '/' + st.total + '</span>' : '');
    });
    h += '</div>';
    return page('Модуль 2. Ассортимент', h);
  };

  routes['page'] = function (id) {
    var p = VA.assortPages.filter(function (x) { return x.id === id; })[0]; if (!p) return notFound();
    setTimeout(function () { var t = $('#mnnTable'); if (t) t.innerHTML = mnnTable(); });
    return page(esc(p.title), '<div class="card">' + p.body + '</div>', { back: '#/assort' });
  };

  function mnnTable() {
    var rows = D().assort, map = {};
    rows.forEach(function (r) { var k = (r.mnn || '— МНН не указано').trim().toLowerCase(); (map[k] = map[k] || []).push(r); });
    var keys = Object.keys(map).sort();
    var h = '<div class="table-wrap"><table><tr><th>МНН</th><th>Торговые названия</th><th>Форма</th><th>Дозировка</th></tr>';
    if (!keys.length) {
      h += '<tr><td colspan="4" class="muted">Пока пусто. Добавьте позиции в «Мой ассортимент» — и таблица заполнится сама.</td></tr>';
      for (var i = 0; i < 4; i++) h += '<tr><td>&nbsp;</td><td></td><td></td><td></td></tr>';
    }
    keys.forEach(function (k) {
      map[k].forEach(function (r, i) {
        h += '<tr>' + (i === 0 ? '<td rowspan="' + map[k].length + '"><b>' + esc(r.mnn || '—') + '</b></td>' : '') + '<td>' + esc(r.name) + '</td><td>' + esc(r.form) + '</td><td>' + esc(r.dose) + '</td></tr>';
      });
    });
    return h + '</table></div><p class="muted">Синонимы — это строки с одинаковыми МНН, дозировкой и формой.</p>';
  }

  routes['group'] = function (id) {
    var g = groupById(id); if (!g) return notFound();
    var h = '<p>' + esc(g.intro) + '</p>';
    h += '<div class="box check"><b>Важно про статус и дозировки</b>Названия ниже — примеры для ориентира. Статус отпуска, дозировки и возраст проверяйте по ГРЛС и инструкции конкретной позиции. Наличие в вашей аптеке — в «Моём ассортименте».</div>';
    h += '<h2>Основные МНН и примеры торговых названий</h2>';
    g.items.forEach(function (it) {
      h += '<div class="card" style="padding:12px 14px"><b>' + esc(it.tn) + '</b>' + (it.chk ? ' <span class="badge warn">проверить по источнику</span>' : '') +
        '<br><small class="muted">МНН / состав:</small> ' + esc(it.mnn) + '<br><small class="muted">Формы:</small> ' + esc(it.forms) +
        '<br><small class="muted">Внимание:</small> ' + esc(it.att) + '</div>';
    });
    h += '<h2>Кому нельзя без врача / тревожные признаки</h2><div class="box important"><ul>' + g.warn.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('') + '</ul></div>';
    h += '<h2>Частые вопросы и как отвечать этично</h2>' + g.faq.map(function (f) { return '<details><summary>' + esc(f.q) + '</summary><p>' + esc(f.a) + '</p></details>'; }).join('');
    h += '<div class="grid two"><div class="card"><h3>Что сопутствует (без навязывания)</h3><ul>' + g.cross.map(function (c) { return '<li>' + esc(c) + '</li>'; }).join('') + '</ul></div>' +
      '<div class="card"><h3>На что смотреть в инструкции</h3><ul>' + g.instr.map(function (c) { return '<li>' + esc(c) + '</li>'; }).join('') + '</ul></div></div>';
    h += '<h2>Тест по группе</h2><div id="quiz"></div>';
    setTimeout(function () {
      quiz($('#quiz'), withIds(g.quiz, 'G:' + g.id + ':', ''), function (r, t) {
        var st = D().groups[g.id] || { best: 0, total: t };
        st.best = Math.max(st.best, r); st.total = t; D().groups[g.id] = st; save();
      });
    });
    return page(esc(g.title), h, { back: '#/assort' });
  };

  routes['test'] = function (kind) {
    var all = allQuestions(), qs, title;
    if (kind === 'wrong') {
      title = 'Повтор ошибок';
      qs = all.filter(function (q) { return D().wrong[q.id]; });
      if (!qs.length) return page(title, '<div class="card"><p>Ошибок для повтора нет. Пройдите уроки и тесты по группам — вопросы с ошибками появятся здесь.</p><a class="btn primary" href="#/test/mixed">Смешанный тест</a></div>', { back: '#/assort' });
      qs = shuffle(qs).slice(0, 15);
    } else {
      title = 'Смешанный тест';
      qs = shuffle(all).slice(0, 12);
    }
    setTimeout(function () { quiz($('#quiz'), qs, function () { }); });
    return page(title, '<p class="muted">Ответили верно — вопрос уходит из «повтора ошибок».</p><div id="quiz"></div>', { back: '#/assort' });
  };

  /* ---------- Карточки (Лейтнер) ---------- */
  var INTERVAL = { 1: 1, 2: 2, 3: 4, 4: 7, 5: 14 };
  function cardDeck() {
    var src = D().cardSource, out = [];
    if (src !== 'mine') VA.groups.forEach(function (g) {
      g.items.forEach(function (it, i) {
        out.push({ id: 'g:' + g.id + ':' + i, front: it.tn, back: [['МНН / состав', it.mnn], ['Группа', g.title], ['Формы', it.forms], ['Внимание', it.att]], chk: it.chk });
      });
    });
    if (src !== 'base') D().assort.forEach(function (r) {
      if (r.inCards === false) return;
      out.push({ id: 'm:' + r.id, front: r.name + (r.dose ? ' ' + r.dose : ''), back: [['МНН', r.mnn], ['Группа', r.group], ['Форма', r.form], ['Особенности', r.features], ['Место', r.shelf]], mine: true });
    });
    return out;
  }
  function isDue(c) { var s = D().cards[c.id]; return !s || s.due <= store.today(); }

  routes['cards'] = function () {
    var d = D(), deck = cardDeck(), queue = shuffle(deck.filter(isDue)).sort(function (a, b) {
      var A = d.cards[a.id] ? d.cards[a.id].box : 0, B = d.cards[b.id] ? d.cards[b.id].box : 0; return A - B;
    });
    var boxes = [0, 0, 0, 0, 0, 0];
    deck.forEach(function (c) { boxes[d.cards[c.id] ? d.cards[c.id].box : 0]++; });
    var h = '<p>Система Лейтнера: «Знаю» — карточка переходит в следующую коробку и появится позже (через 1, 2, 4, 7, 14 дней). «Не знаю» — в первую коробку, повтор завтра и ещё раз сегодня в конце.</p>' +
      '<div class="card"><div class="row"><label for="src" style="margin:0">Колода</label><select id="src" style="flex:1;min-width:160px">' +
      [['all', 'Всё'], ['base', 'Базовая (примеры групп)'], ['mine', 'Мой ассортимент']].map(function (o) { return '<option value="' + o[0] + '"' + (d.cardSource === o[0] ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('') +
      '</select></div><div class="row" style="margin-top:8px"><label for="goal" style="margin:0">Цель в день</label><input id="goal" type="number" min="5" max="200" value="' + d.cardGoal + '" style="width:90px" inputmode="numeric"></div>' +
      '<p style="margin-bottom:4px">Сегодня: <b id="todayCnt">' + (d.cardLog[store.today()] || 0) + '</b> из ' + d.cardGoal + '</p>' + bar(Math.min(d.cardLog[store.today()] || 0, d.cardGoal), d.cardGoal) +
      '<p class="muted" style="margin-top:8px">Новые: ' + boxes[0] + ' · Коробки 1–5: ' + boxes.slice(1).join(' · ') + '</p></div>' +
      '<div id="flashHost"></div>';
    setTimeout(function () {
      $('#src').addEventListener('change', function () { D().cardSource = this.value; save(); render(); });
      $('#goal').addEventListener('change', function () { D().cardGoal = Math.max(5, Math.min(200, parseInt(this.value, 10) || 20)); save(); render(); });
      runCards($('#flashHost'), queue);
    });
    return page('Карточки', h);
  };

  function runCards(el, queue) {
    var requeued = {};
    function next() {
      if (!queue.length) {
        el.innerHTML = '<div class="card"><h2>На сегодня всё!</h2><p>Карточек к повтору нет. Можно добавить новые позиции в <a href="#/my">«Мой ассортимент»</a>.</p></div>';
        return;
      }
      var c = queue[0];
      el.innerHTML = '<p class="muted">Осталось в очереди: ' + queue.length + '</p><div class="flash"><div class="flash-inner">' +
        '<div class="flash-face"><div class="big">' + esc(c.front) + '</div><p class="muted" style="text-align:center">' + (c.mine ? 'мой ассортимент' : 'пример из группы') + ' · вспомните МНН, группу, форму</p></div>' +
        '<div class="flash-face back">' + c.back.filter(function (b) { return b[1]; }).map(function (b) { return '<p style="margin:.2em 0"><small class="muted">' + b[0] + ':</small> ' + esc(b[1]) + '</p>'; }).join('') +
        (c.chk ? '<p><span class="badge warn">проверить по источнику</span></p>' : '') + '</div></div></div>' +
        '<div class="row"><button class="btn block primary" id="flip">Показать ответ</button></div>' +
        '<div class="row" id="grade" hidden><button class="btn danger" style="flex:1" id="no">Не знаю</button><button class="btn primary" style="flex:1" id="yes">Знаю</button></div>';
      var flash = $('.flash', el);
      $('#flip', el).addEventListener('click', function () { flash.classList.add('flipped'); this.parentNode.hidden = true; $('#grade', el).hidden = false; $('#yes', el).focus(); });
      flash.addEventListener('click', function () { if (!flash.classList.contains('flipped')) $('#flip', el).click(); });
      $('#yes', el).addEventListener('click', function () { grade(c, true); });
      $('#no', el).addEventListener('click', function () { grade(c, false); });
    }
    function grade(c, ok) {
      var d = D(), s = d.cards[c.id] || { box: 1 };
      s.box = ok ? Math.min(5, s.box + 1) : 1;
      s.due = store.today(INTERVAL[s.box]);
      d.cards[c.id] = s;
      var t = store.today(); d.cardLog[t] = (d.cardLog[t] || 0) + 1;
      save();
      queue.shift();
      if (!ok && !requeued[c.id]) { requeued[c.id] = true; queue.push(c); }
      var tc = $('#todayCnt'); if (tc) tc.textContent = d.cardLog[t];
      if (d.cardLog[t] === d.cardGoal) toast('Дневная цель выполнена!');
      next();
    }
    next();
  }

  /* ---------- Мой ассортимент ---------- */
  var FIELDS = [
    { key: 'name', title: 'Название' }, { key: 'mnn', title: 'МНН' }, { key: 'form', title: 'Форма' }, { key: 'dose', title: 'Дозировка' },
    { key: 'group', title: 'Группа' }, { key: 'features', title: 'Особенности' }, { key: 'shelf', title: 'Место на витрине' }, { key: 'notes', title: 'Заметки' }
  ];
  var myState = { q: '', group: '', form: '', edit: null };

  routes['my'] = function () {
    var rows = D().assort;
    var groups = VA.groups.map(function (g) { return g.title; }).concat(['Косметика и гигиена', 'БАД', 'Другое']);
    var forms = {}; rows.forEach(function (r) { if (r.form) forms[r.form] = 1; });
    var h = '<p>Это главный способ выучить ассортимент <b>именно вашей аптеки</b>: внесите позиции с витрины (без цен и внутренних данных работодателя), а потом учите их карточками.</p>' +
      '<div class="row no-print"><button class="btn primary" id="addBtn">+ Добавить позицию</button><span class="spacer"></span>' +
      '<button class="btn small" id="csvOut">Экспорт CSV</button><label class="btn small" style="margin:0">Импорт CSV<input type="file" id="csvIn" accept=".csv,text/csv" hidden></label>' +
      '<button class="btn small ghost" id="csvTpl">Шаблон CSV</button></div>' +
      '<div id="formHost"></div>' +
      '<div class="card"><label for="mq">Поиск</label><input id="mq" type="search" placeholder="название, МНН, место…" value="' + esc(myState.q) + '">' +
      '<div class="grid two"><div><label for="mg">Группа</label><select id="mg"><option value="">Все</option>' + groups.map(function (g) { return '<option' + (myState.group === g ? ' selected' : '') + '>' + esc(g) + '</option>'; }).join('') + '</select></div>' +
      '<div><label for="mf">Форма</label><select id="mf"><option value="">Все</option>' + Object.keys(forms).sort().map(function (f) { return '<option' + (myState.form === f ? ' selected' : '') + '>' + esc(f) + '</option>'; }).join('') + '</select></div></div></div>' +
      '<div id="myList"></div>';
    setTimeout(function () {
      drawMyList();
      $('#mq').addEventListener('input', function () { myState.q = this.value; drawMyList(); });
      $('#mg').addEventListener('change', function () { myState.group = this.value; drawMyList(); });
      $('#mf').addEventListener('change', function () { myState.form = this.value; drawMyList(); });
      $('#addBtn').addEventListener('click', function () { openForm(null, groups); });
      $('#csvOut').addEventListener('click', function () {
        if (!store.download('moy-assortiment-' + store.today() + '.csv', store.toCSV(D().assort, FIELDS), 'text/csv;charset=utf-8')) toast('Не удалось скачать файл');
      });
      $('#csvTpl').addEventListener('click', function () {
        store.download('shablon-assortiment.csv', store.toCSV([{ name: 'Учебин', mnn: 'условин', form: 'таблетки', dose: '500 мг', group: 'Боль и жар', features: 'пример строки — удалите', shelf: 'витрина 2, полка 3', notes: '' }], FIELDS), 'text/csv;charset=utf-8');
      });
      $('#csvIn').addEventListener('change', function () { importCSV(this.files[0]); this.value = ''; });
      if (myState.edit) openForm(myState.edit === 'new' ? null : myState.edit, groups);
    });
    return page('Мой ассортимент', h, { back: '#/assort' });
  };

  function filteredMy() {
    var q = myState.q.trim().toLowerCase();
    return D().assort.filter(function (r) {
      if (myState.group && r.group !== myState.group) return false;
      if (myState.form && r.form !== myState.form) return false;
      if (!q) return true;
      return FIELDS.some(function (f) { return String(r[f.key] || '').toLowerCase().indexOf(q) >= 0; });
    }).sort(function (a, b) { return String(a.name).localeCompare(String(b.name), 'ru'); });
  }

  function drawMyList() {
    var el = $('#myList'); if (!el) return;
    var rows = filteredMy(), total = D().assort.length;
    if (!total) { el.innerHTML = '<div class="card"><p>Пока пусто. Начните с 5 позиций, которые чаще всего спрашивают в вашей аптеке.</p></div>'; return; }
    el.innerHTML = '<p class="muted">Показано: ' + rows.length + ' из ' + total + '</p>' + rows.map(function (r) {
      return '<div class="card" style="padding:12px 14px"><div class="row"><b style="flex:1">' + esc(r.name) + (r.dose ? ' · ' + esc(r.dose) : '') + '</b>' +
        (r.inCards === false ? '<span class="badge">не в карточках</span>' : '<span class="badge acc">в карточках</span>') + '</div>' +
        '<small class="muted">МНН:</small> ' + esc(r.mnn || '—') + ' · <small class="muted">Форма:</small> ' + esc(r.form || '—') + ' · <small class="muted">Группа:</small> ' + esc(r.group || '—') +
        (r.shelf ? '<br><small class="muted">Место:</small> ' + esc(r.shelf) : '') + (r.features ? '<br><small class="muted">Особенности:</small> ' + esc(r.features) : '') +
        (r.notes ? '<br><small class="muted">Заметки:</small> ' + esc(r.notes) : '') +
        '<div class="row end no-print" style="margin-top:6px"><button class="btn small" data-edit="' + r.id + '">Изменить</button><button class="btn small danger" data-del="' + r.id + '">Удалить</button></div></div>';
    }).join('');
    $$('[data-edit]', el).forEach(function (b) { b.addEventListener('click', function () { myState.edit = b.getAttribute('data-edit'); render(); }); });
    $$('[data-del]', el).forEach(function (b) {
      b.addEventListener('click', function () {
        if (!confirm('Удалить позицию?')) return;
        var id = b.getAttribute('data-del'); D().assort = D().assort.filter(function (r) { return r.id !== id; }); delete D().cards['m:' + id]; save(); drawMyList(); toast('Удалено');
      });
    });
  }

  function openForm(id, groups) {
    var r = id ? D().assort.filter(function (x) { return x.id === id; })[0] : null;
    if (id && !r) { myState.edit = null; return; }
    r = r || { inCards: true };
    var host = $('#formHost');
    host.innerHTML = '<form class="card" id="myForm"><h2>' + (id ? 'Изменить позицию' : 'Новая позиция') + '</h2>' +
      '<p class="muted">Без цен, наценок и любых внутренних данных работодателя.</p>' +
      inp('name', 'Название (торговое) *', r.name) + inp('mnn', 'МНН', r.mnn) +
      '<div class="grid two">' + inp('form', 'Форма выпуска', r.form, 'таблетки, сироп…') + inp('dose', 'Дозировка / фасовка', r.dose, '500 мг №20') + '</div>' +
      '<label for="f-group">Группа</label><select id="f-group" name="group"><option value="">—</option>' + groups.map(function (g) { return '<option' + (r.group === g ? ' selected' : '') + '>' + esc(g) + '</option>'; }).join('') + '</select>' +
      '<label for="f-features">Особенности</label><textarea id="f-features" name="features" placeholder="кому нельзя без врача, на что смотреть в инструкции, хранение…">' + esc(r.features) + '</textarea>' +
      inp('shelf', 'Место на витрине', r.shelf, 'витрина 3, полка 2') +
      '<label for="f-notes">Заметки</label><textarea id="f-notes" name="notes">' + esc(r.notes) + '</textarea>' +
      '<label class="check-row"><input type="checkbox" name="inCards"' + (r.inCards !== false ? ' checked' : '') + '> Учить в карточках</label>' +
      '<div class="row"><button class="btn primary" type="submit">Сохранить</button><button class="btn ghost" type="button" id="cancelF">Отмена</button></div></form>';
    function inp(k, t, v, ph) { return '<label for="f-' + k + '">' + t + '</label><input type="text" id="f-' + k + '" name="' + k + '" value="' + esc(v) + '"' + (ph ? ' placeholder="' + esc(ph) + '"' : '') + '>'; }
    var f = $('#myForm');
    f.scrollIntoView({ block: 'start' });
    $('#cancelF').addEventListener('click', function () { myState.edit = null; host.innerHTML = ''; });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var o = {}; FIELDS.forEach(function (fl) { o[fl.key] = (f.elements[fl.key].value || '').trim(); });
      o.inCards = f.elements.inCards.checked;
      if (!o.name) { toast('Укажите название'); return; }
      if (id) { Object.assign(r, o); } else { o.id = store.uid(); D().assort.push(o); }
      save(); myState.edit = null; host.innerHTML = ''; drawMyList(); toast('Сохранено');
    });
  }

  function importCSV(file) {
    if (!file) return;
    var rd = new FileReader();
    rd.onload = function () {
      try {
        var rows = store.parseCSV(String(rd.result));
        if (rows.length < 2) throw new Error('В файле нет строк с данными.');
        var head = rows[0].map(function (h) { return h.trim().toLowerCase(); });
        var idx = {};
        FIELDS.forEach(function (f) {
          var i = head.indexOf(f.title.toLowerCase()); if (i < 0) i = head.indexOf(f.key); if (i >= 0) idx[f.key] = i;
        });
        if (!('name' in idx)) throw new Error('Нет столбца «Название».');
        var existing = {}; D().assort.forEach(function (r) { existing[[r.name, r.dose, r.form].join('|').toLowerCase()] = 1; });
        var added = 0, skipped = 0;
        rows.slice(1).forEach(function (cells) {
          var o = { id: store.uid(), inCards: true };
          FIELDS.forEach(function (f) { o[f.key] = idx[f.key] != null ? String(cells[idx[f.key]] || '').trim() : ''; });
          if (!o.name) return;
          var k = [o.name, o.dose, o.form].join('|').toLowerCase();
          if (existing[k]) { skipped++; return; }
          existing[k] = 1; D().assort.push(o); added++;
        });
        save(); render(); toast('Добавлено: ' + added + (skipped ? ', пропущено повторов: ' + skipped : ''));
      } catch (e) { toast('Ошибка импорта: ' + e.message); }
    };
    rd.onerror = function () { toast('Не удалось прочитать файл'); };
    rd.readAsText(file, 'utf-8');
  }

  /* ---------- Тренажёр ---------- */
  routes['trainer'] = function (id, mode) {
    if (id) {
      setTimeout(function () {
        VA.trainer.start($('#trainerHost'), id, mode, function (sid, m, score) {
          if (sid === 'free') return;
          var t = D().trainer[sid] || {}; t[m] = Math.max(t[m] || 0, score); D().trainer[sid] = t; save();
        });
      });
      return page('Тренажёр «Касса»', '<div id="trainerHost"></div>', { back: '#/trainer' });
    }
    var d = D();
    var h = '<p>Учебная касса на вымышленных товарах и условных ценах. Сначала проходите сценарий с подсказками, потом — без подсказок для самопроверки.</p>';
    VA.trainer.scenarios.forEach(function (s) {
      var t = d.trainer[s.id] || {};
      h += '<div class="card"><div class="row"><h3 style="margin:0;flex:1">' + esc(s.title) + '</h3>' +
        (t.hints != null ? '<span class="badge acc">с подск.: ' + t.hints + '</span>' : '') + (t.nohints != null ? '<span class="badge ok">без подск.: ' + t.nohints + '</span>' : '') + '</div>' +
        '<p class="muted">' + esc(s.desc) + '</p><div class="row">' +
        (s.free ? '<a class="btn primary" href="#/trainer/free/hints">Открыть</a>' :
          '<a class="btn primary" href="#/trainer/' + s.id + '/hints">С подсказками</a><a class="btn" href="#/trainer/' + s.id + '/nohints">Без подсказок</a>') + '</div></div>';
    });
    return page('Тренажёр «Касса»', h, { back: '#/1c' });
  };

  /* ---------- Модуль 3 ---------- */
  routes['more'] = function () {
    var h = '<h2>Модуль 3. План и поддержка</h2><div class="grid two">' +
      tile('#/plan', 'План на 14 дней', '20–30 минут в день') +
      tile('#/glossary', 'Словарь терминов', VA.glossary.length + ' терминов') +
      tile('#/cheat', 'Шпаргалка на смену', 'Печатная версия') +
      tile('#/talk', 'Сценарии общения', 'Диалоги-упражнения') +
      tile('#/notes', 'Мои заметки', D().notes.length + ' заметок') +
      tile('#/questions', 'Вопросы наставнику', D().questions.filter(function (q) { return !q.done; }).length + ' открытых') + '</div>' +
      '<h2>Тесты и тренажёр</h2><div class="grid two">' +
      tile('#/trainer', 'Тренажёр «Касса»', '7 сценариев') + tile('#/test/mixed', 'Смешанный тест', '') + tile('#/test/wrong', 'Повтор ошибок', '') + tile('#/1c', 'Уроки 1С', '') + '</div>' +
      '<h2>Данные</h2><div class="grid two">' + tile('#/backup', 'Резервная копия', 'Экспорт и импорт прогресса и заметок') + tile('#/about', 'Об этом сайте', 'Источники и ограничения') + '</div>';
    return page('Ещё', h);
  };

  routes['plan'] = function () {
    var d = D();
    var h = '<p>Каждый день — 2–3 коротких задания. Отмечайте выполненные. Если день пропущен — просто продолжайте со следующего невыполненного.</p>';
    VA.plan.forEach(function (day) {
      var done = day.tasks.filter(function (t, i) { return d.plan['d' + day.day + '-' + i]; }).length;
      h += '<details' + (done < day.tasks.length && !h.match(/<details open/) ? ' open' : '') + '><summary>День ' + day.day + ' · ' + esc(day.theme) + '&nbsp;<span class="badge ' + (done === day.tasks.length ? 'ok' : '') + '">' + done + '/' + day.tasks.length + '</span></summary><ul style="list-style:none;padding:0">' +
        day.tasks.map(function (t, i) {
          var k = 'd' + day.day + '-' + i;
          return '<li><label class="check-row"><input type="checkbox" data-plan="' + k + '"' + (d.plan[k] ? ' checked' : '') + '> <span><a href="' + t.link + '">' + esc(t.t) + '</a></span></label></li>';
        }).join('') + '</ul></details>';
    });
    return page('План на 14 дней', h, { back: '#/more' });
  };

  routes['glossary'] = function () {
    var h = '<input type="search" id="gq" placeholder="Найти термин…" aria-label="Поиск по словарю"><dl class="gloss" id="gl"></dl>';
    setTimeout(function () {
      function draw() {
        var q = $('#gq').value.trim().toLowerCase();
        var list = VA.glossary.filter(function (g) { return !q || (g[0] + ' ' + g[1]).toLowerCase().indexOf(q) >= 0; });
        $('#gl').innerHTML = list.length ? list.map(function (g) { return '<dt>' + esc(g[0]) + '</dt><dd>' + esc(g[1]) + '</dd>'; }).join('') : '<p class="muted">Ничего не найдено.</p>';
      }
      $('#gq').addEventListener('input', draw); draw();
    });
    return page('Словарь терминов', h, { back: '#/more' });
  };

  routes['cheat'] = function () {
    var h = '<div class="row no-print"><button class="btn primary" id="printBtn">Печать / сохранить в PDF</button></div>' + VA.cheat +
      '<p class="muted">Учебная шпаргалка. Порядок действий в вашей аптеке определяется инструкциями работодателя.</p>';
    setTimeout(function () { $('#printBtn').addEventListener('click', function () { window.print(); }); });
    return page('Шпаргалка на смену', h, { back: '#/more' });
  };

  routes['talk'] = function (id) {
    if (!id) {
      var h = '<p>Выберите ответ фармацевта. После выбора — разбор. Цель — уточнять, вежливо отказывать и мягко направлять к врачу.</p><div class="grid">';
      VA.talks.forEach(function (t) { h += tile('#/talk/' + t.id, esc(t.title), '', D().scen[t.id] ? '<span class="badge ok">пройден</span>' : ''); });
      return page('Сценарии общения', h + '</div>', { back: '#/more' });
    }
    var t = VA.talks.filter(function (x) { return x.id === id; })[0]; if (!t) return notFound();
    setTimeout(function () { runTalk($('#talk'), t); });
    return page(esc(t.title), '<div id="talk"></div>', { back: '#/talk' });
  };

  function runTalk(el, t) {
    var step = 0, mistakes = 0, log = '';
    function draw() {
      if (step >= t.steps.length) {
        D().scen[t.id] = true; save();
        el.innerHTML = log + '<div class="card"><h2>Диалог завершён</h2><p>' + (mistakes ? 'Неудачных вариантов: ' + mistakes + '. Перечитайте разборы выше.' : 'Все ответы удачные!') + '</p><div class="row"><a class="btn primary" href="#/talk">К сценариям</a><button class="btn" id="again">Ещё раз</button></div></div>';
        $('#again', el).addEventListener('click', function () { step = 0; mistakes = 0; log = ''; draw(); });
        return;
      }
      var s = t.steps[step];
      el.innerHTML = log + '<div class="bubble them"><small class="muted">Покупатель</small><br>' + esc(s.them) + '</div><div class="opts">' +
        s.opts.map(function (o, i) { return '<button class="opt" data-i="' + i + '">' + esc(o.t) + '</button>'; }).join('') + '</div><div id="tfb"></div>';
      $$('.opt', el).forEach(function (b) {
        b.addEventListener('click', function () {
          var o = s.opts[parseInt(b.getAttribute('data-i'), 10)];
          if (o.ok) {
            log += '<div class="bubble them"><small class="muted">Покупатель</small><br>' + esc(s.them) + '</div><div class="bubble me"><small class="muted">Вы</small><br>' + esc(o.t) + '</div><div class="okmsg">' + esc(o.fb) + '</div>';
            step++; draw();
          } else {
            mistakes++; b.classList.add('wrong'); b.disabled = true;
            $('#tfb', el).innerHTML = '<div class="err">' + esc(o.fb) + ' Попробуйте другой вариант.</div>';
          }
        });
      });
    }
    draw();
  }

  routes['notes'] = function () {
    var h = '<form class="card no-print" id="nf"><label for="nt">Новая заметка</label><textarea id="nt" placeholder="Что узнала сегодня, где что лежит, как делается операция в нашей программе…"></textarea>' +
      '<div class="row end"><button class="btn primary" type="submit">Добавить</button></div></form><div id="nl"></div>' +
      '<p class="muted">Не записывайте сюда персональные данные покупателей и внутренние документы работодателя.</p>';
    setTimeout(function () {
      function draw() {
        var list = D().notes.slice().sort(function (a, b) { return b.created - a.created; });
        $('#nl').innerHTML = list.length ? list.map(function (n) {
          return '<div class="card"><small class="muted">' + new Date(n.updated || n.created).toLocaleString('ru-RU') + '</small><textarea data-n="' + n.id + '" aria-label="Текст заметки">' + esc(n.text) + '</textarea>' +
            '<div class="row end"><button class="btn small danger" data-del="' + n.id + '">Удалить</button></div></div>';
        }).join('') : '<p class="muted">Заметок пока нет.</p>';
        $$('[data-n]').forEach(function (ta) {
          ta.addEventListener('change', function () { var n = D().notes.filter(function (x) { return x.id === ta.getAttribute('data-n'); })[0]; if (n) { n.text = ta.value; n.updated = Date.now(); save(); toast('Сохранено'); } });
        });
        $$('#nl [data-del]').forEach(function (b) { b.addEventListener('click', function () { if (confirm('Удалить заметку?')) { var id = b.getAttribute('data-del'); D().notes = D().notes.filter(function (x) { return x.id !== id; }); save(); draw(); } }); });
      }
      $('#nf').addEventListener('submit', function (e) { e.preventDefault(); var v = $('#nt').value.trim(); if (!v) return; D().notes.push({ id: store.uid(), text: v, created: Date.now() }); save(); $('#nt').value = ''; draw(); });
      draw();
    });
    return page('Мои заметки', h, { back: '#/more' });
  };

  routes['questions'] = function () {
    var h = '<form class="card no-print" id="qf"><label for="qt">Вопрос наставнику</label><textarea id="qt" placeholder="Например: как у нас оформляется возврат? Где отчёт по срокам?"></textarea>' +
      '<div class="row end"><button class="btn primary" type="submit">Добавить</button></div></form><div id="ql"></div>';
    setTimeout(function () {
      function draw() {
        var list = D().questions.slice().sort(function (a, b) { return (a.done - b.done) || (b.created - a.created); });
        $('#ql').innerHTML = list.length ? list.map(function (q) {
          return '<div class="card"' + (q.done ? ' style="opacity:.7"' : '') + '><label class="check-row"><input type="checkbox" data-done="' + q.id + '"' + (q.done ? ' checked' : '') + '> <b>' + esc(q.text) + '</b></label>' +
            '<label for="qa-' + q.id + '">Ответ</label><textarea id="qa-' + q.id + '" data-ans="' + q.id + '">' + esc(q.answer) + '</textarea>' +
            '<div class="row end"><button class="btn small danger" data-del="' + q.id + '">Удалить</button></div></div>';
        }).join('') : '<p class="muted">Вопросов пока нет. Записывайте всё, что непонятно, — и задавайте на смене.</p>';
        function find(id) { return D().questions.filter(function (x) { return x.id === id; })[0]; }
        $$('[data-done]').forEach(function (c) { c.addEventListener('change', function () { var q = find(c.getAttribute('data-done')); q.done = c.checked; save(); draw(); }); });
        $$('[data-ans]').forEach(function (ta) { ta.addEventListener('change', function () { var q = find(ta.getAttribute('data-ans')); q.answer = ta.value; save(); toast('Сохранено'); }); });
        $$('#ql [data-del]').forEach(function (b) { b.addEventListener('click', function () { if (confirm('Удалить вопрос?')) { var id = b.getAttribute('data-del'); D().questions = D().questions.filter(function (x) { return x.id !== id; }); save(); draw(); } }); });
      }
      $('#qf').addEventListener('submit', function (e) { e.preventDefault(); var v = $('#qt').value.trim(); if (!v) return; D().questions.push({ id: store.uid(), text: v, answer: '', done: false, created: Date.now() }); save(); $('#qt').value = ''; draw(); });
      draw();
    });
    return page('Вопросы наставнику', h, { back: '#/more' });
  };

  routes['backup'] = function () {
    var h = '<p>Прогресс, заметки, вопросы, «Мой ассортимент» и карточки хранятся <b>только в этом браузере</b>. Если очистить данные браузера или сменить телефон — они пропадут. Раз в несколько дней сохраняйте резервную копию.</p>' +
      '<div class="card"><h2>Сохранить копию</h2><p>Один файл .json со всеми данными. Храните его у себя (например, в «Файлах» телефона).</p>' +
      '<div class="row"><button class="btn primary" id="expBtn">Скачать резервную копию</button><button class="btn" id="expShow">Показать как текст</button></div><div id="expText"></div></div>' +
      '<div class="card"><h2>Восстановить из копии</h2><p>Текущие данные на этом устройстве будут <b>заменены</b> данными из файла.</p>' +
      '<label class="btn" style="margin:0">Выбрать файл .json<input type="file" id="impFile" accept=".json,application/json" hidden></label>' +
      '<details><summary>Вставить текст копии вручную</summary><textarea id="impText" placeholder="Вставьте сюда текст резервной копии"></textarea><button class="btn" id="impTextBtn">Восстановить из текста</button></details></div>' +
      '<div class="card"><h2>Сбросить всё</h2><p>Удалит весь прогресс и записи на этом устройстве.</p><button class="btn danger" id="resetBtn">Сбросить</button></div>';
    setTimeout(function () {
      function json() { return JSON.stringify(store.exportObject(), null, 1); }
      $('#expBtn').addEventListener('click', function () {
        if (store.download('vika-aptek-kopiya-' + store.today() + '.json', json(), 'application/json')) toast('Файл сохранён в «Загрузки»');
        else showText();
      });
      function showText() {
        $('#expText').innerHTML = '<textarea readonly id="expTa" style="min-height:160px">' + esc(json()) + '</textarea><button class="btn small" id="copyBtn">Скопировать</button>';
        $('#copyBtn').addEventListener('click', function () {
          var ta = $('#expTa'); ta.select();
          var done = function () { toast('Скопировано'); };
          try { if (navigator.clipboard) navigator.clipboard.writeText(ta.value).then(done, function () { document.execCommand('copy'); done(); }); else { document.execCommand('copy'); done(); } } catch (e) { toast('Выделите текст и скопируйте вручную'); }
        });
      }
      $('#expShow').addEventListener('click', showText);
      function doImport(text) {
        try {
          var obj = JSON.parse(text);
          if (!confirm('Заменить текущие данные данными из копии?')) return;
          store.importObject(obj); toast('Данные восстановлены'); location.hash = '#/';
        } catch (e) { toast('Не получилось: ' + (e.message || 'файл повреждён')); }
      }
      $('#impFile').addEventListener('change', function () {
        var f = this.files[0]; if (!f) return; var rd = new FileReader();
        rd.onload = function () { doImport(String(rd.result)); }; rd.readAsText(f, 'utf-8'); this.value = '';
      });
      $('#impTextBtn').addEventListener('click', function () { doImport($('#impText').value); });
      $('#resetBtn').addEventListener('click', function () {
        if (confirm('Точно удалить весь прогресс и записи?') && confirm('Это нельзя отменить. Удалить?')) { store.reset(); toast('Сброшено'); location.hash = '#/'; }
      });
    });
    return page('Резервная копия', h, { back: '#/more' });
  };

  routes['about'] = function () {
    var h = '<div class="card"><h2>Для чего этот сайт</h2><p>Личный учебный помощник для старта работы фармацевтом: общая логика учётной программы, тренажёр кассы, ассортимент, общение с покупателем. Работает без интернета, ничего никуда не отправляет.</p></div>' +
      '<div class="card"><h2>Что сайт не заменяет</h2><ul><li>Обучение у работодателя и инструкции аптеки.</li><li>Наставника и старшего смены.</li><li>Инструкции к препаратам и официальные реестры.</li><li>Действующие нормативные документы.</li></ul></div>' +
      '<div class="card"><h2>Где проверять</h2><ul>' +
      '<li>Государственный реестр лекарственных средств — grls.rosminzdrav.ru (регистрация, инструкции, условия отпуска, взаимозаменяемость, предельные цены ЖНВЛП).</li>' +
      '<li>Перечень ЖНВЛП — действующее распоряжение Правительства РФ (publication.pravo.gov.ru).</li>' +
      '<li>Правила отпуска и оформления рецептов, правила хранения, надлежащая аптечная практика — приказы Минздрава России (publication.pravo.gov.ru).</li>' +
      '<li>Маркировка — официальный сайт системы «Честный знак».</li>' +
      '<li>Медицинские изделия — реестр Росздравнадзора.</li></ul>' +
      '<p>Пометка <span class="badge warn">проверить по источнику</span> означает, что сведения нужно сверить: статус мог измениться или зависит от конкретной позиции.</p></div>' +
      '<div class="card"><h2>Примеры и данные</h2><p>Товары в тренажёре и примеры в уроках («Термоглин», «Условин-Учеб», «Учебин» и т. п.) — вымышленные. Цены — условные единицы. Названия реальных препаратов в Модуле 2 приведены только как общеизвестные примеры торговых названий для запоминания МНН.</p></div>';
    return page('Об этом сайте', h, { back: '#/more' });
  };

  function notFound() { return page('Страница не найдена', '<p><a href="#/">На главную</a></p>'); }

  /* ---------- Роутер ---------- */
  function render() {
    var hash = location.hash.replace(/^#\/?/, '');
    var parts = hash.split('/').map(function (p) { try { return decodeURIComponent(p); } catch (e) { return p; } });
    var name = parts[0] || '';
    var fn = routes[name] || notFound;
    app.innerHTML = fn(parts[1], parts[2]);
    var navKey = { '': 'home', '1c': '1c', lesson: '1c', trainer: '1c', assort: 'assort', page: 'assort', group: 'assort', my: 'assort', test: 'assort', cards: 'cards' }[name] || 'more';
    $$('.bottomnav a', document).forEach(function (a) {
      var on = a.getAttribute('data-nav') === navKey; a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    $$('[data-plan]').forEach(function (c) {
      c.addEventListener('change', function () { D().plan[c.getAttribute('data-plan')] = c.checked; save(); });
    });
  }
  var lastRoute = null;
  window.addEventListener('hashchange', function () {
    var r = location.hash.split('/')[1] || '';
    if (r !== 'my') myState.edit = null;
    render();
    if (lastRoute !== location.hash) { window.scrollTo(0, 0); app.focus({ preventScroll: true }); }
    lastRoute = location.hash;
  });

  /* ---------- Тема ---------- */
  var themeBtn = document.getElementById('themeBtn');
  function applyTheme(t) {
    if (t === 'auto') document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', t);
  }
  themeBtn.addEventListener('click', function () {
    var order = ['auto', 'light', 'dark'], cur = store.getTheme(), nx = order[(order.indexOf(cur) + 1) % 3];
    store.setTheme(nx); applyTheme(nx);
    toast('Тема: ' + { auto: 'как в системе', light: 'светлая', dark: 'тёмная' }[nx]);
  });

  VA.render = render;
  render();
})();
