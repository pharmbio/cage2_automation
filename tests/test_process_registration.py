import pytest

from lab_adaption import config
from laborchestrator.orchestrator_implementation import (
    Orchestrator as OrchestratorImplementation,
)
from laborchestrator.pythonlab_process_finder import ProcessFinder


def _process_id(process):
    return f"{process.module.__name__}.{process.name}"


def _configured_worker_type():
    return getattr(config, "worker_type", config.Worker)


PROCESSES = ProcessFinder.get_processes(config.process_module)


def test_process_discovery_finds_processes():
    assert PROCESSES


@pytest.mark.parametrize("importable_process", PROCESSES, ids=_process_id)
def test_process_can_be_added_to_and_removed_from_orchestrator(importable_process):
    orchestrator = OrchestratorImplementation(
        reader="PythonLab",
        worker_type=_configured_worker_type(),
    )
    orchestrator.schedule_manager.time_limit_short = config.default_scheduling_time

    process = ProcessFinder.create_process(importable_process)
    process_name = importable_process.name

    added_name = orchestrator.add_process(
        process_object=process,
        name=process_name,
    )

    assert added_name == process_name
    assert process_name in {
        process_info.name for process_info in orchestrator.processes
    }

    assert orchestrator.remove_processes([process_name])
    assert process_name not in {
        process_info.name for process_info in orchestrator.processes
    }
