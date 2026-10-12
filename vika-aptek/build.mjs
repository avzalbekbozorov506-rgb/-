// Сборка одного самодостаточного файла: node build.mjs → dist/vika-aptek.html
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const src = join(root, 'src');
let html = readFileSync(join(src, 'index.html'), 'utf8');

const csp = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data: blob:; connect-src \'none\'; form-action \'none\'; base-uri \'none\'">';
html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + csp);

html = html.replace(/<link rel="stylesheet" href="([^"]+)">/g, (_, f) =>
  '<style>\n' + readFileSync(join(src, f), 'utf8') + '</style>');

html = html.replace(/<script src="([^"]+)"><\/script>/g, (_, f) => {
  const code = readFileSync(join(src, f), 'utf8');
  if (code.includes('</script')) throw new Error('В ' + f + ' встречается </script — сборка сломает файл');
  return '<script>\n' + code + '</script>';
});

if (/(src|href)="(https?:)?\/\//.test(html)) throw new Error('Найдена внешняя ссылка на ресурс');

mkdirSync(join(root, 'dist'), { recursive: true });
writeFileSync(join(root, 'dist', 'vika-aptek.html'), html);
console.log('OK: dist/vika-aptek.html, ' + Math.round(Buffer.byteLength(html) / 1024) + ' КБ');
