#!/bin/bash
set -e

# use the virtual environment that is active in the calling shell
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ No virtual environment active. Activate the one you installed lab_adaption into first." >&2
    exit 1
fi

echo "🔹 Starting services in separate gnome-terminal tabs..."

gnome-terminal --tab --title="Scheduler" \
    -- bash -c "source $VIRTUAL_ENV/bin/activate && labscheduler; exec bash" &

gnome-terminal --tab --title="DB Server" \
    -- bash -c "source $VIRTUAL_ENV/bin/activate && run_db_server; exec bash" &

gnome-terminal --tab --title="Orchestrator" \
    -- bash -c "source $VIRTUAL_ENV/bin/activate && laborchestrator; exec bash" &

gnome-terminal --tab --title="SILA Servers" \
    -- bash -c "source $VIRTUAL_ENV/bin/activate && start_sila_servers; exec bash" &

echo "✅ All service tabs launched."
