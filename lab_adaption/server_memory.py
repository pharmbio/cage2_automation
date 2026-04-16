import json
import logging
from pathlib import Path

from sila2.client import SilaClient


class ServerMemory:
    def __init__(self):
        self._file = Path(__file__).with_name("known_servers.json")
        self._known_servers = self._load()

    def load_from_memory(self, server_name: str) -> SilaClient | None:
        known_server = self._known_servers.get(server_name)
        if not known_server:
            return None

        address, port = known_server
        try:
            client = SilaClient(address=address, port=port, insecure=True)
            name = client.SiLAService.ServerName.get()
            if name != server_name:
                logging.error(
                    f"The server on {address}:{port} is {name} instead of {server_name}"
                )
                self._forget(server_name)
                return None
            return client
        except Exception as ex:
            logging.warning(
                f"Failed to connect to cached server for {server_name} on {address}:{port}: {ex}"
            )
            self._forget(server_name)
            return None

    def memorize(self, client: SilaClient) -> None:
        server_name = client.SiLAService.ServerName.get()
        self._known_servers[server_name] = (client.address, int(client.port))
        self._save()

    def _load(self) -> dict[str, tuple[str, int]]:
        try:
            if not self._file.exists():
                return {}
            with self._file.open() as handle:
                raw_data = json.load(handle)
            return {
                server_name: (address, int(port))
                for server_name, (address, port) in raw_data.items()
            }
        except Exception as ex:
            logging.warning(f"Failed to load known servers from {self._file}: {ex}")
            return {}

    def _save(self) -> None:
        try:
            with self._file.open("w") as handle:
                json.dump(self._known_servers, handle, indent=2, sort_keys=True)
        except Exception as ex:
            logging.warning(f"Failed to save known servers to {self._file}: {ex}")

    def _forget(self, server_name: str) -> None:
        removed = self._known_servers.pop(server_name, None)
        if removed is not None:
            self._save()
