#!/usr/bin/env bash
#
# Push the current schedule live.
#
#   ./scripts/publish.sh                    # "update the schedule"
#   ./scripts/publish.sh "friday sci-fi"    # your own note
#
# Vercel deploys on push, so the site is live within a minute or so.

set -euo pipefail
cd "$(dirname "$0")/.."

message="${1:-update the schedule}"

if ! git remote get-url origin >/dev/null 2>&1; then
    echo "No 'origin' remote is configured, so there is nowhere to publish to." >&2
    echo "Create the repo on GitHub, then:" >&2
    echo "  git remote add origin git@github.com:USERNAME/thiagotv.git" >&2
    exit 1
fi

# Regenerate the crawlable pages before anything is committed. Doing it here
# rather than by hand is what keeps the static pages from drifting out of sync
# with playlist.json -- a stale programme page is worse than none, because it
# gets indexed.
echo "Building programme pages..."
python3 scripts/build.py
echo

if [[ -z "$(git status --porcelain)" ]]; then
    echo "Nothing has changed since the last publish."
    exit 0
fi

echo "Publishing:"
git status --short
echo

git add -A
git commit -q -m "$message"

# Let push failures speak for themselves. Auth problems, a rejected
# non-fast-forward and a dead network all land here and all need different
# fixes, so print git's own words rather than a guess at what went wrong.
if ! git push origin main; then
    echo >&2
    echo "Push failed -- the commit is saved locally but the site is NOT updated." >&2
    echo "Fix whatever git reported above, then run this script again." >&2
    exit 1
fi

echo
echo "Published. Vercel usually has it live within a minute."
echo "https://thiagotv.vercel.app"
