#!/bin/bash
set -e

VENV_NAME="test_venv"

echo "🔹 Starting services in separate gnome-terminal tabs..."

gnome-terminal --tab --title="Scheduler" \
    -- bash -c "source $PWD/$VENV_NAME/bin/activate && labscheduler; exec bash" &

gnome-terminal --tab --title="DB Server" \
    -- bash -c "source $PWD/$VENV_NAME/bin/activate && run_db_server; exec bash" &

gnome-terminal --tab --title="Orchestrator" \
    -- bash -c "source $PWD/$VENV_NAME/bin/activate && laborchestrator; exec bash" &

gnome-terminal --tab --title="SILA Servers" \
    -- bash -c "source $PWD/$VENV_NAME/bin/activate && start_sila_servers; exec bash" &

echo "✅ All service tabs launched."
