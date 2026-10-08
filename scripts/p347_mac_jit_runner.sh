#!/bin/bash
set -euo pipefail

REPO="${P347_GITHUB_REPO:-nz-genesis/ci-probe}"
LABEL="${P347_RUNNER_LABEL:-p347-mac}"
ROOT="${P347_RUNNER_ROOT:-$HOME/.p347-mac-runner}"
RUNNER_NAME="${P347_RUNNER_NAME:-$(scutil --get ComputerName 2>/dev/null || hostname)-p347}"

GH_BIN=""
for candidate in \
  "$(command -v gh 2>/dev/null || true)" \
  "/opt/homebrew/bin/gh" \
  "/usr/local/bin/gh" \
  "$HOME/.local/bin/gh"
do
  if [[ -n "$candidate" && -x "$candidate" ]]; then
    GH_BIN="$candidate"
    break
  fi
done

if [[ -z "$GH_BIN" ]]; then
  echo "ERROR: GitHub CLI (gh) is required."
  echo "Install it, authenticate once with: gh auth login"
  exit 2
fi

if ! "$GH_BIN" auth status >/dev/null 2>&1; then
  echo "ERROR: gh is not authenticated for the LaunchAgent user."
  echo "Run: gh auth login as the same macOS user."
  exit 2
fi

mkdir -p "$ROOT"
cd "$ROOT"

echo "== P347 Mac JIT runner bootstrap =="
echo "Repository: $REPO"
echo "Runner label: $LABEL"
echo "Runner root: $ROOT"
echo "Runner name: $RUNNER_NAME"

ARCH="$(uname -m)"
case "$ARCH" in
  arm64) ASSET_ARCH="arm64" ;;
  x86_64) ASSET_ARCH="x64" ;;
  *) echo "ERROR: unsupported macOS architecture: $ARCH"; exit 2 ;;
esac

RELEASE_JSON="$("$GH_BIN" api repos/actions/runner/releases/latest)"
VERSION="$(printf '%s' "$RELEASE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"].lstrip("v"))')"
ASSET_NAME="$(printf '%s' "$RELEASE_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); a=[x["name"] for x in d["assets"] if "osx-'$ASSET_ARCH'" in x["name"] and x["name"].endswith(".tar.gz")]; print(a[0] if a else "")')"

if [[ -z "$ASSET_NAME" ]]; then
  echo "ERROR: could not find macOS runner asset for $ASSET_ARCH."
  exit 2
fi

echo "Runner version: $VERSION"
echo "Runner asset: $ASSET_NAME"

if [[ ! -x "$ROOT/run.sh" ]]; then
  curl --fail --location --proto '=https' --tlsv1.2 \
    "https://github.com/actions/runner/releases/download/v$VERSION/$ASSET_NAME" \
    -o "$ROOT/runner.tar.gz"
  tar -xzf "$ROOT/runner.tar.gz" -C "$ROOT"
  rm -f "$ROOT/runner.tar.gz"
fi

echo
echo "The runner will be JIT/ephemeral: one workflow job, then GitHub removes it."
echo "No GitHub token is written to disk by this script."
echo

while true; do
  JIT_CONFIG="$(
    gh api --method POST \
      -H 'Accept: application/vnd.github+json' \
      "repos/$REPO/actions/runners/generate-jitconfig" \
      -f "name=$RUNNER_NAME" \
      -f "labels[]=self-hosted" \
      -f "labels[]=macOS" \
      -f "labels[]=$LABEL" \
      --jq '.encoded_jit_config'
  )"

  if [[ -z "$JIT_CONFIG" ]]; then
    echo "ERROR: GitHub returned no JIT configuration."
    exit 3
  fi

  echo "Waiting for a trusted P347 job..."
  "$ROOT/run.sh" --jitconfig "$JIT_CONFIG" || true

  echo "Job finished; preparing a fresh ephemeral runner."
  sleep 2
done
