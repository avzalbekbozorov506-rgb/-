#!/usr/bin/env bash
# Видео для ShapelessAI через GitHub Pages (ветка gh-pages, сайт https://avzalbekbozorov506-rgb.github.io/-/).
#   bash publish_pages.sh add <имя>  — кладёт hq/<имя>_hq.mp4 в gh-pages/v/<имя>.mp4, ждёт, пока сайт отдаст файл, печатает ссылку
#   bash publish_pages.sh rm <имя>   — удаляет файл после fetch_asset (видео в ветке не храним)
set -e; cd "$(dirname "$0")/.."; act=$1; n=$2; W=$(mktemp -d)/ghp
git fetch -q origin gh-pages && git worktree add -q --detach "$W" FETCH_HEAD
trap 'git worktree remove --force "$W"' EXIT
cd "$W"; mkdir -p v
if [ "$act" = add ]; then cp "$OLDPWD/reels/hq/${n}_hq.mp4" "v/$n.mp4"; git add -f "v/$n.mp4"; msg="Видео $n для публикации"
else git rm -q "v/$n.mp4"; msg="Видео $n удалено после загрузки"; fi
git commit -qm "$msg" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q origin HEAD:gh-pages
[ "$act" = add ] || exit 0
U="https://avzalbekbozorov506-rgb.github.io/-/v/$n.mp4"
for i in $(seq 60); do [ "$(curl -s -o /dev/null -w '%{http_code}' -r 0-99 "$U")" = 206 ] && { echo "$U"; exit 0; }; sleep 10; done
echo "сайт не отдал файл за 10 мин: $U" >&2; exit 1
