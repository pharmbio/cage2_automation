#! bin/bash

cd source

packages = ("laborchestrator", "pythonlabscheduler", "pythonLab", "platform_status_db")
for dir in "{packages[@]}"; do
    cd "$dir"
    git pull
    cd ..
done

cd ..