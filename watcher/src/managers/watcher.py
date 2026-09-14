import logging
import re
import threading
from typing import Any

from docker.types import CancellableStream

import docker
from src.managers.messenger import APIMessenger

logger = logging.getLogger(__name__)

ROUTER_RULE_PATTERN = re.compile(r"^traefik\.http\.routers\.[^.]+\.rule$")
HOST_PATTERN = re.compile(r"Host\((.*?)\)")


class DockerWatcher:
    """
    Listens to Docker events and uses the messenger to send updates to the API.
    """

    messanger: APIMessenger
    is_running: bool
    _docker_client: docker.DockerClient
    _thread: threading.Thread | None
    _events: CancellableStream[dict[str, Any]] | None
    _labels_cache: dict[str, list[str]]

    def __init__(self, messenger: APIMessenger):
        self.messenger = messenger
        self.is_running = False
        self._docker_client = docker.from_env()
        self._thread = None
        self._events = None
        self._labels_cache = {}

    def start(self):
        """
        Start listening for Docker events.
        """

        if self.is_running:
            logger.debug("DockerWatcher is already running - skipping start.")
            return

        self.is_running = True

        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stop listening for Docker events.
        """

        if not self.is_running:
            logger.debug("DockerWatcher is not running - skipping stop.")
            return

        self.is_running = False

        if self._events is not None:
            self._events.close()

        if self._thread is not None:
            self._thread.join()

        self._thread = None

    def sync(self):
        """
        Retrieve current Docker containers state and run updates to synchronize the DNS.
        """
        containers = self._docker_client.containers.list()

        for container in containers:
            container_id = container.id

            if container_id is None:
                return

            self._labels_cache[container_id] = self._get_container_hosts(container)

        self.messenger.sync([host for hosts in self._labels_cache.values() for host in hosts])

    def _listen(self):
        """
        Main loop listening for Docker events.
        """

        try:
            self._events = self._docker_client.events(
                filters={"type": "container"},
                decode=True,
            )

            for event in self._events:
                if not self.is_running:
                    break

                action = event.get("Action")

                if action == "start":
                    self._on_container_start(event)
                elif action == "die":
                    self._on_container_die(event)

        except Exception:
            logger.exception("Docker event listener failed.")

        finally:
            self._events = None
            self.is_running = False

    def _on_container_start(self, event):
        container_id = event["Actor"]["ID"]

        container = self._docker_client.containers.get(container_id)

        self._labels_cache[container_id] = self._get_container_hosts(container)

        for hostname in self._labels_cache[container_id]:
            self.messenger.update(hostname)

    def _get_container_hosts(self, container):
        labels: dict[str, str] = container.labels

        all_hosts = []

        for key, value in labels.items():
            if not ROUTER_RULE_PATTERN.match(key):
                continue

            hosts = [host.strip().strip("`'\"") for match in HOST_PATTERN.findall(value) for host in match.split(",")]

            all_hosts.extend(hosts)

        return all_hosts

    def _on_container_die(self, event):
        container_id = event["Actor"]["ID"]

        hostnames = self._labels_cache.get(container_id)

        if not hostnames:
            return

        for hostname in hostnames:
            logger.info(hostname)
            self.messenger.delete(hostname)
