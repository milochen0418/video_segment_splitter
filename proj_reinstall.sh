#!/usr/bin/env bash
set -euo pipefail

SHOW_HELP=false
REMOVE_ONLY=false
WITH_RERUN=false
WITH_RERUN_DEBUG=false

# Recreate the uv env (.venv) and clear Reflex build artifacts.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
  echo "[proj_reinstall] $*"
}

usage() {
  cat <<'EOF'
Usage: ./proj_reinstall.sh [options]

Options:
  --help, -h       Show this help and exit.
  --remove-only     Remove the project's .venv and clean artifacts; skip creating a new env and installing deps.
  --with-rerun      After install, run: uv run ./reflex_rerun.sh
  --with-rerun-debug  After install, run: uv run ./reflex_rerun.sh --loglevel debug
EOF
}

require_uv() {
  if ! command -v uv >/dev/null 2>&1; then
    log "uv is required but not found on PATH (brew install uv)."
    exit 1
  fi
}

clean_reflex_artifacts() {
  log "Cleaning Reflex build artifacts and caches"
  rm -rf "$ROOT_DIR/.web" "$ROOT_DIR/.states"
  rm -rf "$ROOT_DIR/assets/external"
  find "$ROOT_DIR" -name "__pycache__" -type d -prune -exec rm -rf {} +
  find "$ROOT_DIR" -maxdepth 1 -name "*.db" -type f -delete
}

clean_uploads() {
  log "Removing uploaded files"
  rm -rf "$ROOT_DIR/uploaded_files"
}

remove_venv() {
  if [[ -d "$ROOT_DIR/.venv" ]]; then
    log "Removing $ROOT_DIR/.venv"
    rm -rf "$ROOT_DIR/.venv"
  else
    log "No .venv found"
  fi
}

recreate_venv() {
  # uv takes the Python version from .python-version (downloading it if it
  # is not installed) and re-locks by itself when pyproject.toml has changed.
  log "Creating .venv with uv (Python $(cat "$ROOT_DIR/.python-version"))"
  log "Installing dependencies"
  (cd "$ROOT_DIR" && uv sync)
}

parse_args() {
  while (($#)); do
    case "$1" in
      --help|-h)
        SHOW_HELP=true
        ;;
      --remove-only)
        REMOVE_ONLY=true
        ;;
      --with-rerun)
        WITH_RERUN=true
        ;;
      --with-rerun-debug)
        WITH_RERUN_DEBUG=true
        ;;
      *)
        log "Unknown argument: $1"
        usage
        exit 1
        ;;
    esac
    shift
  done
}

main() {
  parse_args "$@"

  if $SHOW_HELP; then
    usage
    exit 0
  fi

  require_uv
  clean_reflex_artifacts
  clean_uploads
  remove_venv
  if $REMOVE_ONLY; then
    log "Remove-only mode: skipping env creation and dependency install"
    exit 0
  fi
  recreate_venv
  if $WITH_RERUN_DEBUG; then
    log "Running reflex_rerun.sh via uv (debug)"
    (cd "$ROOT_DIR" && uv run ./reflex_rerun.sh --loglevel debug)
  elif $WITH_RERUN; then
    log "Running reflex_rerun.sh via uv"
    (cd "$ROOT_DIR" && uv run ./reflex_rerun.sh)
  fi
  log "Done"
}

main "$@"