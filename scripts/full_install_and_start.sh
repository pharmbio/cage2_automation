#!/bin/bash
set -e

# --- Variables ---
REPO_URL="https://gitlab.com/OpenLabAutomation/adaption-template.git"
DB_REPO_URL="https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git"
VENV_NAME="test_venv"
SUPERUSER_NAME="admin"
SUPERUSER_PASS="password"
SUPERUSER_EMAIL=""

# --- Step 1: Clone main repository ---
echo "🔹 Step 1: Cloning main repository..."
if [ ! -d "adaption-template" ]; then
    git clone "$REPO_URL"
fi
cd adaption-template
echo "✅ Repository ready."

# --- Step 2: Create virtual environment ---
echo "🔹 Step 2: Creating Python virtual environment '$VENV_NAME'..."
if [ ! -d "$VENV_NAME" ]; then
    python3 -m venv "$VENV_NAME"
fi
source "$VENV_NAME/bin/activate"
echo "✅ Virtual environment activated."

# --- Step 3: Install dependencies ---
echo "🔹 Step 3: Installing dependencies..."
uv pip install -r requirements.txt -e .
uv pip install -r requirements_servers.txt
uv pip install -r requirements_mip_cp.txt
echo "✅ Dependencies installed."

# --- Step 4: Clone & install database package ---
echo "🔹 Step 4: Setting up database package..."
if [ ! -d "platform_status_db" ]; then
    git clone "$DB_REPO_URL"
fi
uv pip install -e platform_status_db/.
echo "✅ Database package installed (branch $DB_BRANCH)."

# --- Step 4a: Initialize database (non-interactive) ---
echo "🔹 Step 4a: Initializing database (migrate + superuser)..."
cd platform_status_db/src/platform_status_db

python manage.py migrate --noinput
DJANGO_SUPERUSER_USERNAME=$SUPERUSER_NAME \
DJANGO_SUPERUSER_PASSWORD=$SUPERUSER_PASS \
DJANGO_SUPERUSER_EMAIL=$SUPERUSER_EMAIL \
python manage.py createsuperuser --noinput || true

cd ../../..
echo "✅ Database initialized with superuser '$SUPERUSER_NAME'."

# --- Step 4b: Fill the database ---
echo "🔹 Step 4b: Filling database with lab setup..."
python scripts/add_lab_setup_to_db.py
echo "✅ Lab setup added to database."

# --- Step 5: Startup in new tabs ---
echo "🔹 Step 5: Starting services in new tabs..."
bash start_services.sh

echo "🎉 All done! Your environment is ready and services are running."
