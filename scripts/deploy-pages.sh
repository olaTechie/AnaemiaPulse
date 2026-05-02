#!/usr/bin/env bash
set -euo pipefail

REPO_REMOTE="${REPO_REMOTE:-anaemia-pulse}"
BRANCH="${BRANCH:-main}"
SITE_URL="https://olatechie.github.io/AnaemiaPulse/"

if ! git remote get-url "$REPO_REMOTE" >/dev/null 2>&1; then
  echo "Remote '$REPO_REMOTE' is not configured."
  echo "Add it with: git remote add $REPO_REMOTE https://github.com/olaTechie/AnaemiaPulse.git"
  exit 1
fi

echo "Running checks..."
npm run lint
npm run build

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "There are uncommitted changes. Commit them before deploying."
  git status --short
  exit 1
fi

echo "Pushing $BRANCH to $REPO_REMOTE..."
git push "$REPO_REMOTE" "$BRANCH"

echo "GitHub Actions will publish the site automatically:"
echo "$SITE_URL"
