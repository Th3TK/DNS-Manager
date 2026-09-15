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
RETRY_SYNC_INTERVAL_SECONDS = 60


class DockerWatcher:
    """
    Listens to Docker events and uses the messenger to send updates to the API.
    """

    messanger: APIMessenger
    is_running: bool
    _sync_active: bool
    _docker_client: docker.DockerClient
    _thread: threading.Thread | None
    _sync_thread: threading.Thread | None
    _events: CancellableStream[dict[str, Any]] | None
    _labels_cache: dict[str, list[str]]

    def __init__(self, messenger: APIMessenger):
        self.messenger = messenger
        self.is_running = False
        self._sync_active = False
        self._docker_client = docker.from_env()
        self._thread = None
        self._sync_thread = None
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

        self._thread = threading.Thread(target=self.__listen, daemon=True)
        self._thread.start()

    def start_sync(self):
        if self._sync_active:
            logger.debug("Docker synchronization is already running - skipping.")
            return

        self._sync_thread = threading.Thread(target=self.__sync, daemon=True)
        self._sync_thread.start()

    def __sync(self):
        """Retrieve current Docker containers state and synchronize the DNS."""

        if self._sync_active:
            return

        self._sync_active = True

        # Retry synchronizing every RETRY_SYNC_INTERVAL_SECONDS
        while self.is_running and not self.messenger.is_synchronized:
            # retrieve all current containers
            containers = self._docker_client.containers.list()

            # update cache
            self._labels_cache = {}

            for container in containers:
                if container.id is not None:
                    self._labels_cache[container.id] = self._get_container_host_values(container)

            # get hostnames from updated cache
            hostnames = [hostname for hosts in self._labels_cache.values() for hostname in hosts]

            # send SYNC to the API
            self.messenger.sync(hostnames)

            if self.messenger.is_synchronized:
                break

            # wait for next retry
            threading.Event().wait(RETRY_SYNC_INTERVAL_SECONDS)

        self._sync_active = False

    def __listen(self):
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

                if not self.messenger.is_synchronized:
                    self.start_sync()

        except Exception:
            logger.exception("Docker event listener failed.")

        finally:
            self._events = None
            self.is_running = False

    def _on_container_start(self, event):
        container_id = event["Actor"]["ID"]

        container = self._docker_client.containers.get(container_id)

        self._labels_cache[container_id] = self._get_container_host_values(container)

        for hostname in self._labels_cache[container_id]:
            self.messenger.update(hostname)

    def _on_container_die(self, event):
        container_id = event["Actor"]["ID"]

        hostnames = self._labels_cache.pop(container_id, None)

        if not hostnames:
            return

        for hostname in hostnames:
            self.messenger.delete(hostname)

    def _get_container_host_values(self, container):
        labels: dict[str, str] = container.labels

        all_hosts = []

        for key, value in labels.items():
            if not ROUTER_RULE_PATTERN.match(key):
                continue

            hosts = [host.strip().strip("`'\"") for match in HOST_PATTERN.findall(value) for host in match.split(",")]

            all_hosts.extend(hosts)

        return all_hosts
