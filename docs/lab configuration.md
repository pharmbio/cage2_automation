# Lab Configuration

Your lab is configured in two files in the `lab_adaption` folder:

- **`platform_config.yaml`** — describes the physical resources in your lab (storage, movers, humans, etc.) and their capacities.
- **`config.py`** — describes how the orchestrator should start up: which worker to use, which processes to load, which scheduling algorithm to run, and how to connect to the database.

## `platform_config.yaml`

This file lists every device/resource in your lab, grouped by category, and tells the scheduler how many things each resource can handle at once.

```yaml
description:
    - "An exemplary robotic lab description. Add devices at will"
sila_servers:
    storage:
        Hotel1:
            capacity: 20
        Hotel2:
            capacity: 20
        Hotel3:
            capacity: 20
    movers:
        GenericArm:
            capacity: 1
    humans:
        Human:
            process_capacity: 99 # can do multitasking?
            capacity: 2  # has two hands
    greeters:
        Greeter:
            capacity: 1
            process_capacity: 1

pythonlab_translation:
    storage: LabwareStorageResource
    movers: MoverServiceResource
    humans: HumanServiceResource
    greeters: GreeterServiceResource
```

### `sila_servers`

Each entry under `sila_servers` is a category (e.g. `storage`, `movers`, `humans`, `greeters`) containing one or more named devices. Add, remove, or rename devices here to match the hardware and staff available in your lab. Each device takes:

| Field | Meaning                                                                                                                                                                                                |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `capacity` | How many labware items/slots the device can hold or handle at the same time (e.g. a storage hotel with `capacity: 20` has 20 slots; a robot arm with `capacity: 1` can carry one item).                |
| `process_capacity` *(optional)* | How many processes the device/person can do in parallel. Defaults to matching `capacity` if omitted.

You can add as many categories and devices as you need — this list should reflect everything the scheduler is allowed to plan work around.

### `pythonlab_translation`

This section maps each category above to the PythonLab resource class used in your process descriptions (see the [PythonLab api reference](pythonlab/api_reference.md)). The keys here must match the categories used under `sila_servers`, and the values must match the resource classes your workflows expect. If you add a new category to `sila_servers`, add a matching line here so the orchestrator knows how to interpret it in your processes.

## `config.py`

This file controls how the orchestrator starts up. It's a plain Python file — uncomment or edit the lines you need; anything left out falls back to a sensible default.

| Setting | What it does |
|---|---|
| `db_client` | Which database to use for tracking labware. Set to `None` to run without a database. |
| `worker_type` | Which worker drives execution. Leave as-is to just run a simulation; point it at your own worker implementation to control real hardware. |
| `lab_config_file` | Path to your `platform_config.yaml`. Change this if you rename or move the file. |
| `default_scheduling_time` | How many seconds the scheduler is given to compute a new schedule by default. Can also be changed later from the orchestrator GUI. |
| `scheduling_algorithm` | Which scheduling algorithm to use (e.g. `BottleneckPD`). |
| `process_module` | Which Python module contains your process descriptions (see [pythonLab introduction](pythonlab/processes.md)). |
| `arm_open` | Whether the robotic arm view is shown by default in the orchestrator GUI. |
| `db_open` | Whether the labware database view is shown by default in the orchestrator GUI. |
| `browser_open` | Whether the SiLA browser view is shown by default in the orchestrator GUI. |

After changing `platform_config.yaml`, remember to rerun the database setup script so the new resources are picked up (see the [quickstart](quickstart.md#running-with-python)).
