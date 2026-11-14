#!/bin/bash
# Pull the latest version of every package the cage2 platform runs.
#
# The repo list mirrors lab_adaption/terminator_config (the directories the
# terminals cd into) and the dependencies in pyproject.toml. Keep them in sync
# when a terminal or dependency is added.
#
# Usage: ./update_all.sh            (uses ~/labautomation/automation as venv)
#        VENV=/path/to/venv ./update_all.sh

BASE="${BASE:-$HOME/labautomation}"
VENV="${VENV:-$BASE/automation}"
CAGE2_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPOS=(
    "$CAGE2_DIR"
    "$CAGE2_DIR/platform_status_db"
    "$BASE/packages/source/scheduler"
    "$BASE/sila_servers/genericroboticarm"
    "$BASE/sila_servers/echo"
    "$BASE/sila_servers/sealer"
    "$BASE/sila_servers/barcodereader"
    "$BASE/sila_servers/cytomat2C"
    "$BASE/sila_servers/liconic"
    "$BASE/sila_servers/multiflowfx"
    "$BASE/sila_servers/bluewasher"
    "$BASE/sila_servers/washer405"
    "$BASE/sila_servers/squid"
)

failed=()
skipped=()

# --- Step 1: git pull every checkout ---
for repo in "${REPOS[@]}"; do
    name="${repo#"$BASE"/}"
    if [ ! -d "$repo/.git" ]; then
        echo "⚠️  $name: not a git checkout, skipping"
        skipped+=("$name")
        continue
    fi
    branch="$(git -C "$repo" branch --show-current)"
    echo "🔹 $name [$branch]"
    # fast-forward if possible, otherwise try an automatic merge commit
    if ! git -C "$repo" pull --no-rebase --no-edit; then
        if git -C "$repo" rev-parse -q --verify MERGE_HEAD >/dev/null; then
            # merge conflict: undo it so the checkout is left as it was
            git -C "$repo" merge --abort
            echo "❌ $name: merge conflict, aborted - merge manually"
        else
            echo "❌ $name: pull failed (uncommitted changes in the way or no network?)"
        fi
        failed+=("$name")
    fi
done

# --- Step 2: upgrade pip-installed dependencies from pyproject.toml ---
if [ ! -x "$VENV/bin/python" ]; then
    echo "❌ venv not found at $VENV, skipping pip upgrades"
    failed+=("pip upgrades")
else
    PY="$VENV/bin/python"
    # uv is much faster; fall back to pip when it is not installed
    if command -v uv >/dev/null; then
        PIP=(uv pip)
        PIP_TARGET=(--python "$PY")
    else
        PIP=("$PY" -m pip)
        PIP_TARGET=()
    fi
    editable="$("${PIP[@]}" list "${PIP_TARGET[@]}" --editable --format=freeze 2>/dev/null | cut -d= -f1 | tr '[:upper:]_' '[:lower:]-')"

    # uu* packages (pythonlab, labscheduler, laborchestrator), read from
    # pyproject.toml after the pull so new pins are respected.
    # The SiLA servers and cage2 are installed editable, so the git pull above covers them.
    mapfile -t deps < <("$PY" - "$CAGE2_DIR/pyproject.toml" <<'EOF'
import re, sys, tomllib
with open(sys.argv[1], "rb") as f:
    deps = tomllib.load(f)["project"]["dependencies"]
for d in deps:
    name = re.split(r"[\s<>=!~@\[;]", d, maxsplit=1)[0]
    if name.lower().startswith("uu"):
        print(f"{name}\t{d}")
EOF
)

    specs=()
    for line in "${deps[@]}"; do
        name="${line%%$'\t'*}"
        spec="${line#*$'\t'}"
        norm="$(echo "$name" | tr '[:upper:]_' '[:lower:]-')"
        if grep -qx "$norm" <<<"$editable"; then
            echo "🔹 $name is installed editable, covered by git pull"
            continue
        fi
        specs+=("$spec")
    done

    # one call, so dependencies are resolved once for all packages
    if [ ${#specs[@]} -gt 0 ]; then
        echo "🔹 upgrading with ${PIP[*]}: ${specs[*]}"
        "${PIP[@]}" install "${PIP_TARGET[@]}" --upgrade "${specs[@]}" || failed+=("pip upgrades")
    fi
fi

# --- Summary ---
echo
[ ${#skipped[@]} -gt 0 ] && echo "⚠️  skipped: ${skipped[*]}"
if [ ${#failed[@]} -gt 0 ]; then
    echo "❌ failed: ${failed[*]}"
    exit 1
fi
echo "✅ everything up to date"
