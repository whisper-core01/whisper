#!/usr/bin/env bash
set -euo pipefail

# finalize_whisper_repo.sh
#
# Purpose:
#   Prepare the WHISPER GitHub repository for reviewer / grant review.
#
# What it does:
#   - archives the old manifesto README;
#   - installs the reviewer-ready README if present;
#   - creates documentation folders;
#   - checks expected docs/code/tests/bench files;
#   - keeps Protocol Labs-specific docs under docs/protocol-labs;
#   - keeps simulation schemas under schemas/ if present;
#   - runs validation commands when possible;
#   - prints a final git commit/tag command.
#
# Usage:
#   cd /path/to/whisper
#   chmod +x finalize_whisper_repo.sh
#   ./finalize_whisper_repo.sh
#
# Optional:
#   If your generated files are in another folder:
#   DOCS_SRC=/path/to/generated/docs ./finalize_whisper_repo.sh
#
# Notes:
#   This script does not push to GitHub.
#   It does not force a commit.
#   It is safe to re-run.

ROOT="$(pwd)"
DOCS_SRC="${DOCS_SRC:-$ROOT}"
VERSION="${VERSION:-v0.4.3}"

echo "== WHISPER repo finalizer =="
echo "Root:     $ROOT"
echo "Docs src: $DOCS_SRC"
echo "Version:  $VERSION"
echo ""

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: This directory is not a Git repository."
  echo "Run this script from the root of your whisper GitHub repo."
  exit 1
fi

mkdir -p docs/archive
mkdir -p docs/protocol-labs
mkdir -p docs/simulation
mkdir -p scripts
mkdir -p schemas

echo "== 1. Archive current README if needed =="

if [[ -f README.md ]]; then
  if grep -qiE "Genesis of Total Invisibility|Formal Presentation Document|Sovereign, Encrypted Communication System" README.md; then
    ARCHIVE_PATH="docs/archive/FORMAL_PRESENTATION_MAY_2026.md"
    if [[ ! -f "$ARCHIVE_PATH" ]]; then
      mv README.md "$ARCHIVE_PATH"
      echo "Archived old README -> $ARCHIVE_PATH"
    else
      echo "Archive already exists: $ARCHIVE_PATH"
      echo "Keeping current README.md untouched for now."
    fi
  else
    echo "README.md does not look like the old manifesto. Keeping it."
  fi
else
  echo "No README.md found."
fi

echo ""
echo "== 2. Install reviewer-ready README =="

README_CANDIDATES=(
  "$DOCS_SRC/README.md"
  "$DOCS_SRC/README_Whisper_NLnet_PL_ready_v3.md"
  "$DOCS_SRC/whisper_readme_final_v3/README.md"
  "$DOCS_SRC/whisper_readme_final_v2/README.md"
  "$DOCS_SRC/whisper_readme_final/README.md"
)

INSTALLED_README=0
for candidate in "${README_CANDIDATES[@]}"; do
  if [[ -f "$candidate" ]]; then
    # Avoid copying the archived manifesto back if the candidate is the current repo README.
    if grep -qiE "experimental MVP framework|structural divergence|not a secure communication protocol" "$candidate"; then
      if [[ "$(realpath "$candidate")" != "$(realpath README.md 2>/dev/null || echo README.md)" ]]; then
        cp "$candidate" README.md
        echo "Installed reviewer-ready README from: $candidate"
      else
        echo "Reviewer-ready README already installed: $candidate"
      fi
      INSTALLED_README=1
      break
    fi
  fi
done

if [[ "$INSTALLED_README" -eq 0 ]]; then
  echo "WARNING: reviewer-ready README not found."
  echo "Expected one of:"
  printf '  - %s\n' "${README_CANDIDATES[@]}"
fi

echo ""
echo "== 3. Copy root documentation files when available =="

ROOT_DOCS=(
  THREAT_MODEL.md
  WHITEPAPER.md
  WHITEPAPER_v0.2.md
  ROADMAP.md
  SIMULATION_PLAN.md
  PHASE2_VALIDATION_CRITERIA.md
  SIMULATION_REPORT.md
  SIMULATION_REPORT_v0.2.md
  BENCHMARKS.md
  REGRESSION_TESTS.md
  SECURITY.md
  RELEASE_NOTES_v0.4.3.md
  RELEASE_NOTES_v0.4.3_v3.md
  APPLY_NOTES.md
  GRANT_REVIEW_POSITIONING.md
  RESEARCH_PLAN.md
  NIX_REPRODUCIBILITY.md
)

copy_doc() {
  local src="$1"
  local dst="$2"
  if [[ -f "$src" ]]; then
    cp "$src" "$dst"
    echo "Copied $(basename "$src") -> $dst"
    return 0
  fi
  return 1
}

for doc in "${ROOT_DOCS[@]}"; do
  # normalize versioned filenames to canonical names
  case "$doc" in
    WHITEPAPER_v0.2.md)
      [[ -f "$DOCS_SRC/$doc" ]] && copy_doc "$DOCS_SRC/$doc" "WHITEPAPER.md" || true
      ;;
    SIMULATION_REPORT_v0.2.md)
      [[ -f "$DOCS_SRC/$doc" ]] && copy_doc "$DOCS_SRC/$doc" "SIMULATION_REPORT.md" || true
      ;;
    RELEASE_NOTES_v0.4.3_v3.md)
      [[ -f "$DOCS_SRC/$doc" ]] && copy_doc "$DOCS_SRC/$doc" "RELEASE_NOTES_v0.4.3.md" || true
      ;;
    *)
      [[ -f "$DOCS_SRC/$doc" ]] && copy_doc "$DOCS_SRC/$doc" "$doc" || true
      ;;
  esac
done

echo ""
echo "== 4. Copy Protocol Labs docs if available =="

PL_DOCS=(
  PROTOCOL_LABS_ALIGNMENT.md
  PROTOCOL_LABS_REVIEW_RESPONSE.md
  VOXMESH_FRACTAL_COUNT_RATIONALE.md
  SIMULATOR_SCOPE.md
  BASELINE_SPECS.md
)

for doc in "${PL_DOCS[@]}"; do
  if [[ -f "$DOCS_SRC/$doc" ]]; then
    cp "$DOCS_SRC/$doc" "docs/protocol-labs/$doc"
    echo "Copied $doc -> docs/protocol-labs/"
  fi
done

echo ""
echo "== 5. Copy simulation docs if available =="

SIM_DOCS=(
  SIMULATION_PLAN_PATCH_v0.2.md
  SIMULATION_PLAN_DIFF_v0.3.md
  PHASE2_VALIDATION_CRITERIA.md
  SIMULATION_REPORT.md
  SIMULATION_REPORT_v0.2.md
)

for doc in "${SIM_DOCS[@]}"; do
  if [[ -f "$DOCS_SRC/$doc" ]]; then
    target="$doc"
    [[ "$doc" == "SIMULATION_REPORT_v0.2.md" ]] && target="SIMULATION_REPORT.md"
    cp "$DOCS_SRC/$doc" "docs/simulation/$target"
    echo "Copied $doc -> docs/simulation/$target"
  fi
done

echo ""
echo "== 6. Copy JSON schemas if available =="

SCHEMA_SOURCES=(
  "$DOCS_SRC/schemas"
  "$DOCS_SRC/whisper_protocol_labs_hardening/schemas"
)

for schema_dir in "${SCHEMA_SOURCES[@]}"; do
  if [[ -d "$schema_dir" ]]; then
    cp "$schema_dir"/*.schema.json schemas/ 2>/dev/null || true
    echo "Copied schemas from $schema_dir"
  fi
done

echo ""
echo "== 7. Copy Nix/reproducibility files if available =="

REPRO_FILES=(
  flake.nix
  requirements.txt
  .envrc
)

for f in "${REPRO_FILES[@]}"; do
  if [[ -f "$DOCS_SRC/$f" ]]; then
    cp "$DOCS_SRC/$f" "$f"
    echo "Copied $f"
  fi
done

if [[ -f "$DOCS_SRC/scripts/validate_nix_shell.sh" ]]; then
  cp "$DOCS_SRC/scripts/validate_nix_shell.sh" scripts/validate_nix_shell.sh
  chmod +x scripts/validate_nix_shell.sh
  echo "Copied scripts/validate_nix_shell.sh"
fi

# If requirements.txt still missing, create minimal one.
if [[ ! -f requirements.txt ]]; then
  cat > requirements.txt <<'EOF'
pytest>=8.0
EOF
  echo "Created minimal requirements.txt"
fi

echo ""
echo "== 8. Check expected code/test/bench files =="

EXPECTED_CODE=(
  rotor_machine_v01.py
  mce_v01.py
  mce_hardened_v01.py
  loader_v01.py
  bal_v01.py
  dome_v01.py
  voxmesh_v01.py
  lemonade_v01.py
  vault_v01.py
  vault_disk_v01.py
  reticulum_bridge_v01.py
  full_pipeline_v01.py
)

EXPECTED_DIRS=(
  tests
  bench
)

MISSING=0

for f in "${EXPECTED_CODE[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING code: $f"
    MISSING=1
  fi
done

for d in "${EXPECTED_DIRS[@]}"; do
  if [[ ! -d "$d" ]]; then
    echo "MISSING dir:  $d"
    MISSING=1
  fi
done

echo ""
echo "== 9. Check expected documentation =="

EXPECTED_DOCS=(
  README.md
  THREAT_MODEL.md
  WHITEPAPER.md
  ROADMAP.md
  SIMULATION_PLAN.md
  PHASE2_VALIDATION_CRITERIA.md
  SIMULATION_REPORT.md
  BENCHMARKS.md
  REGRESSION_TESTS.md
  SECURITY.md
  RELEASE_NOTES_v0.4.3.md
  APPLY_NOTES.md
)

for f in "${EXPECTED_DOCS[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING doc:  $f"
    MISSING=1
  fi
done

echo ""
echo "== 10. Run validations if possible =="

if [[ -d tests ]]; then
  echo "[validation] pytest -q"
  if command -v pytest >/dev/null 2>&1; then
    pytest -q
  else
    echo "pytest not found. Try: python3 -m pytest -q"
    python3 -m pytest -q || true
  fi

  if [[ -f tests/test_regression_v043.py ]]; then
    echo "[validation] regression suite"
    if command -v pytest >/dev/null 2>&1; then
      pytest -q tests/test_regression_v043.py
    else
      python3 -m pytest -q tests/test_regression_v043.py || true
    fi
  fi
else
  echo "Skipping pytest: tests/ missing."
fi

if [[ -f full_pipeline_v01.py ]]; then
  echo "[validation] full pipeline smoke"
  python3 full_pipeline_v01.py
else
  echo "Skipping full pipeline smoke: full_pipeline_v01.py missing."
fi

if [[ -f bench/bench_full_pipeline.py ]]; then
  echo "[validation] full pipeline benchmark"
  python3 bench/bench_full_pipeline.py --payload-size 1048576
else
  echo "Skipping full pipeline benchmark: bench/bench_full_pipeline.py missing."
fi

echo ""
echo "== 11. Git status =="
git status --short

echo ""
if [[ "$MISSING" -eq 0 ]]; then
  echo "== Repo looks structurally reviewer-ready =="
else
  echo "== Repo still has missing expected files =="
  echo "Review the MISSING lines above before tagging."
fi

echo ""
echo "Suggested commit:"
echo "  git add ."
echo "  git commit -m \"docs: finalize reviewer-ready WHISPER ${VERSION} bundle\""
echo "  git tag ${VERSION}"
echo ""
echo "Push when ready:"
echo "  git push origin main --tags"
