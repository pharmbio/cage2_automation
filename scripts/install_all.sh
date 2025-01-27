#! bin/bash
# create directory if necessary
source_dir="source"
if [ ! -d "$source_dir" ]; then
  echo "Directory '$source_dir' does not exist. Creating it..."
  mkdir "$source_dir"
fi
cd "$source_dir"

curl -LsSf https://astral.sh/uv/install.sh | sh

if [ ! -d "laborchestrator" ]; then
  git clone git@gitlab.com:opensourcelab/laborchestrator.git  # develop
fi
cd laborchestrator
git checkout develop
uv pip install -e .
cd ..
if [ ! -d "pythonlabscheduler" ]; then
  git clone git@gitlab.com:opensourcelab/pythonlabscheduler.git  # develop
fi
cd pythonlabscheduler
git checkout develop
uv pip install -e .
uv pip install --upgrade protobuf  # needed for scheduler
cd ..
if [ ! -d "pythonLab" ]; then
  git clone git@gitlab.com:opensourcelab/pythonLab.git  # feature/labels
fi
cd pythonLab
git checkout feature/labels
uv pip install -e .
cd ..
if [ ! -d "platform_status_db" ]; then
  git clone https://gitlab.com/StefanMa/platform_status_db.git  # develop
fi
cd platform_status_db
git checkout develop
uv pip install -e .
cd ..


# install device connectors
if [ ! -d "devices" ]; then
  mkdir "devices"
fi
cd devices

pairs=(
  "washer git@gitlab.com:uppsala_automation/sila-servers/cell-washer.git"
  "squid git@gitlab.com:uppsala_automation/sila-servers/squid.git"
  "sealer git@gitlab.com:uppsala_automation/sila-servers/cealer.git"
  "robo_arm" "git@gitlab.com:StefanMa/genericroboticarm.git"
  "cytomat2C" "git@gitlab.com:uppsala_automation/sila-servers/cytomat2C.git"
)

# Iterate over each pair (device, repo)
for pair in "${pairs[@]}"; do
  # Split the pair into device and repo
  device=$(echo $pair | cut -d' ' -f1)
  repo=$(echo $pair | cut -d' ' -f2)

  # Check if the device directory exists
  if [ ! -d "$device" ]; then
    echo "Cloning $repo into $device..."
    git clone "$repo" "$device"
    cd "$device"
    uv pip install -e .
    cd ..
  else
    echo "$device already exists, skipping..."
  fi
done

cd ..