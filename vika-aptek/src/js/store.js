/* Хранилище: всё только в localStorage этого браузера. Любой доступ обёрнут в try/catch. */
(function () {
  'use strict';
  var KEY = 'vika-aptek-v1';
  var THEME_KEY = 'vika-aptek-theme';
  var available = true;

  function defaults() {
    return {
      version: 1,
      lessons: {},      // id урока -> { best: число верных, total, done: true }
      groups: {},       // id группы -> { best, total }
      wrong: {},        // id вопроса -> true (для «повтора ошибок»)
      cards: {},        // id карточки -> { box: 1..5, due: 'ГГГГ-ММ-ДД' }
      cardLog: {},      // 'ГГГГ-ММ-ДД' -> сколько карточек повторено
      cardGoal: 20,
      cardSource: 'all',
      plan: {},         // 'd3-1' -> true
      trainer: {},      // id сценария -> { hints: лучший результат, nohints: лучший результат }
      scen: {},         // id диалога -> true, если пройден
      notes: [],        // { id, text, created, updated }
      questions: [],    // { id, text, answer, done, created }
      assort: []        // «Мой ассортимент»
    };
  }

  var data = defaults();
  try {
    var raw = window.localStorage.getItem(KEY);
    if (raw) data = merge(defaults(), JSON.parse(raw));
  } catch (e) {
    available = false;
  }

  function merge(base, extra) {
    if (!extra || typeof extra !== 'object') return base;
    Object.keys(base).forEach(function (k) {
      if (!(k in extra)) return;
      var b = base[k], x = extra[k];
      if (Array.isArray(b)) { if (Array.isArray(x)) base[k] = x; }
      else if (b && typeof b === 'object') { if (x && typeof x === 'object' && !Array.isArray(x)) base[k] = x; }
      else if (typeof x === typeof b) base[k] = x;
    });
    return base;
  }

  function save() {
    try {
      window.localStorage.setItem(KEY, JSON.stringify(data));
      return true;
    } catch (e) {
      available = false;
      return false;
    }
  }

  function today(offsetDays) {
    var d = new Date();
    if (offsetDays) d.setDate(d.getDate() + offsetDays);
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  function uid() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  function exportObject() {
    return { app: 'vika-aptek', exported: new Date().toISOString(), data: data };
  }

  function importObject(obj) {
    if (!obj || obj.app !== 'vika-aptek' || !obj.data || typeof obj.data !== 'object') {
      throw new Error('Это не файл резервной копии этого сайта.');
    }
    data = merge(defaults(), obj.data);
    return save();
  }

  function reset() {
    data = defaults();
    return save();
  }

  function getTheme() {
    try { return window.localStorage.getItem(THEME_KEY) || 'auto'; } catch (e) { return 'auto'; }
  }
  function setTheme(t) {
    try {
      if (t === 'auto') window.localStorage.removeItem(THEME_KEY);
      else window.localStorage.setItem(THEME_KEY, t);
    } catch (e) { /* тема просто не запомнится */ }
  }

  /* ---- CSV (разделитель «;», чтобы Excel в русской локали открывал по столбцам) ---- */
  function csvEscape(v) {
    v = v == null ? '' : String(v);
    if (/[";\n\r]/.test(v)) v = '"' + v.replace(/"/g, '""') + '"';
    return v;
  }
  function toCSV(rows, cols) {
    var out = [cols.map(function (c) { return csvEscape(c.title); }).join(';')];
    rows.forEach(function (r) {
      out.push(cols.map(function (c) { return csvEscape(r[c.key]); }).join(';'));
    });
    return '﻿' + out.join('\r\n');
  }
  function parseCSV(text) {
    text = text.replace(/^﻿/, '');
    var firstLine = text.split(/\r?\n/)[0] || '';
    var sep = (firstLine.split(';').length >= firstLine.split(',').length) ? ';' : ',';
    var rows = [], row = [], cell = '', q = false;
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      if (q) {
        if (ch === '"') {
          if (text[i + 1] === '"') { cell += '"'; i++; } else q = false;
        } else cell += ch;
      } else if (ch === '"') q = true;
      else if (ch === sep) { row.push(cell); cell = ''; }
      else if (ch === '\n' || ch === '\r') {
        if (ch === '\r' && text[i + 1] === '\n') i++;
        row.push(cell); rows.push(row); row = []; cell = '';
      } else cell += ch;
    }
    if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
    return rows.filter(function (r) { return r.some(function (c) { return c.trim() !== ''; }); });
  }

  function download(filename, text, mime) {
    try {
      var blob = new Blob([text], { type: mime || 'application/octet-stream' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url; a.download = filename; a.rel = 'noopener';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
      return true;
    } catch (e) {
      return false;
    }
  }

  window.VA = window.VA || {};
  window.VA.store = {
    get data() { return data; },
    save: save,
    today: today,
    uid: uid,
    isAvailable: function () { return available; },
    exportObject: exportObject,
    importObject: importObject,
    reset: reset,
    getTheme: getTheme,
    setTheme: setTheme,
    toCSV: toCSV,
    parseCSV: parseCSV,
    download: download
  };
})();
