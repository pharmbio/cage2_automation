from types import SimpleNamespace

from lab_adaption.plugins.echo_plugin import EchoPlugin


def test_name_of_removed_process_is_not_reused():
    # the step names of a removed process stay in use (e.g. by the worker), so its name must not come back
    orchestrator = SimpleNamespace(jssp=SimpleNamespace(process_by_name={}))
    plugin = EchoPlugin(orchestrator)
    first = plugin._process_name()
    orchestrator.jssp.process_by_name[first] = None
    second = plugin._process_name()
    assert first != second
    # the first process is removed again
    orchestrator.jssp.process_by_name.pop(first)
    assert plugin._process_name() not in {first, second}
