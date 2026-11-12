import pytest
from laborchestrator.engine.worker_interface import ObservableProtocolHandler

from lab_adaption.device_wrappers import finish_observable_command


class Succeeding(ObservableProtocolHandler):
    def _protocol(self, client, **kwargs):
        pass


class Failing(ObservableProtocolHandler):
    def _protocol(self, client, **kwargs):
        raise RuntimeError("Expected a plate at Liconic_nest while there was none")


def test_successful_command_passes():
    finish_observable_command(Succeeding().run_protocol(None))


def test_failed_command_raises():
    # e.g., a failed GetLabware must stop the following PlacePlate
    with pytest.raises(Exception, match="Expected a plate"):
        finish_observable_command(Failing().run_protocol(None))
