#!/bin/bash
set -e

# --- Variables ---
REPO_URL="https://gitlab.com/OpenLabAutomation/adaption-template.git"
DB_REPO_URL="https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git"
VENV_NAME="test_venv"

# --- Clone main repository ---
if [ ! -d "adaption-template" ]; then
    git clone "$REPO_URL"
fi
cd adaption-template

# --- Create virtual environment ---
if [ ! -d "$VENV_NAME" ]; then
    python3 -m venv "$VENV_NAME"
fi

# Activate venv
source "$VENV_NAME/bin/activate"

# --- Install dependencies ---
uv pip install -r requirements.txt -e .
uv pip install -r requirements_servers.txt
uv pip install -r requirements_mip_cp.txt

# --- Clone & install database package ---
if [ ! -d "platform_status_db" ]; then
    git clone "$DB_REPO_URL"
fi
uv pip install -e platform_status_db/.

# --- Initialize database (will ask for inputs) ---
bash scripts/init_db.sh

# --- Fill the database ---
python scripts/add_lab_setup_to_db.py

# --- Startup commands in new terminal tabs ---
gnome-terminal \
  --tab -- bash -c "source $PWD/$VENV_NAME/bin/activate && labscheduler; exec bash" \
  --tab -- bash -c "source $PWD/$VENV_NAME/bin/activate && python run_db_server; exec bash" \
  --tab -- bash -c "source $PWD/$VENV_NAME/bin/activate && laborchestrator; exec bash" \
  --tab -- bash -c "source $PWD/$VENV_NAME/bin/activate && start_sila_servers; exec bash"

echo "✅ Installation complete. All services have been started in separate tabs."
