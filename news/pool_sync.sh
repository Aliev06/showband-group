#!/usr/bin/env bash
# Xəbər hovuzu (news/pool.json) main-də yox, ayrıca "bot-data" branch-da saxlanır:
# hər saatlıq yığım sayt yenilənməsini (GitHub Pages) işə salmasın.
#   pull — bot-data-dan news/pool.json gətirir;   push — news/pool.json-u bot-data-ya yazır.
set -u
cd "$(dirname "$0")/.."
case "${1:-}" in
  pull)
    git fetch -q --depth 1 origin bot-data 2>/dev/null && git show FETCH_HEAD:pool.json > news/pool.json 2>/dev/null \
      && echo "pool: bot-data-dan gətirildi" || echo "pool: bot-data yoxdur, boş başlayırıq" ;;
  push)
    [ -f news/pool.json ] || exit 0
    T=$(mktemp -d); cp news/pool.json "$T/pool.json"
    (cd "$T" && git init -q && git checkout -q -b bot-data && git add pool.json \
      && git -c user.name=showband-bot -c user.email=bot@users.noreply.github.com commit -qm "pool" ) || exit 0
    # hovuz müvəqqəti vəziyyətdir — tarixçə lazım deyil, son versiya qalib gəlir
    git -C "$T" push -q -f "$(git remote get-url origin)" bot-data 2>/dev/null \
      || git -C "$T" -c http.extraheader="$(git config --get http.https://github.com/.extraheader)" push -q -f "$(git remote get-url origin)" bot-data
    echo "pool: bot-data-ya yazıldı" ;;
esac
