#!/usr/bin/env bash
# Publica las infografías del día en la rama claude/serene-faraday del repo y deja los enlaces directos.
# Uso: bash skills/infografia-nep/publicar.sh <carpeta-con-los-png> <AAAA-MM-DD>
# Usa un worktree aparte para no tocar la rama de las skills. Imprime una URL por PNG.
set -euo pipefail
ORIGEN="$(cd "$1" && pwd)"; FECHA="$2"
RAMA="claude/serene-faraday"
REPO="$(git rev-parse --show-toplevel)"
PUB="$(mktemp -d)/pub"
cd "$REPO"
if git fetch -q origin "$RAMA" 2>/dev/null; then git worktree add -q --detach "$PUB" FETCH_HEAD
else git worktree add -q --detach "$PUB" HEAD; fi
mkdir -p "$PUB/infografias/$FECHA"
cp "$ORIGEN"/*.png "$ORIGEN"/*.json "$PUB/infografias/$FECHA/" 2>/dev/null || cp "$ORIGEN"/*.png "$PUB/infografias/$FECHA/"
cd "$PUB"
git add "infografias/$FECHA"
git -c user.name="${GIT_AUTHOR_NAME:-Rutina NEP}" -c user.email="${GIT_AUTHOR_EMAIL:-foreman1204@gmail.com}" \
  commit -q -m "infografía $FECHA"
git push -q origin "HEAD:refs/heads/$RAMA"
SHA="$(git rev-parse HEAD)"
URL="$(git -C "$REPO" remote get-url origin | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##; s#^.*github.com/##')"
for f in "infografias/$FECHA"/*.png; do echo "https://raw.githubusercontent.com/$URL/$SHA/$f"; done
cd "$REPO" && git worktree remove --force "$PUB"
