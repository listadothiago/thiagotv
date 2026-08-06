#!/usr/bin/env bash
#
# Push the current schedule live.
#
#   ./scripts/publish.sh                    # "update the schedule"
#   ./scripts/publish.sh "friday sci-fi"    # your own note
#
# GitHub Pages rebuilds on push, so the site is live within a minute or so.

set -euo pipefail
cd "$(dirname "$0")/.."

message="${1:-update the schedule}"

if [[ -z "$(git status --porcelain)" ]]; then
    echo "Nothing has changed since the last publish."
    exit 0
fi

echo "Publishing:"
git status --short

git add -A
git commit -q -m "$message"
git push -q origin main

remote_url="$(git remote get-url origin)"
echo
echo "Pushed. GitHub Pages usually takes under a minute to rebuild."
echo "Repo: ${remote_url}"
