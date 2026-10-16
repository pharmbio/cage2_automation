from laborchestrator.gui.plugins import PluginInterface
from laborchestrator.logging_manager import StandardLogger as Logger


class EchoPlugin(PluginInterface):
    def get_name(self) -> str:
        return "Echo"

    def add_process_clicked(self):
        Logger.info(f"{self.get_name()} plugin: adding processes is not implemented yet")
