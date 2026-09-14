import asyncio
import logging
from typing import Literal

import requests

from src.config import ENV_CONFIG
from src.utils.env import get_env
from src.utils.paths import join_url

type Action = Literal["UPDATE", "DELETE"]

RETRY_INTERVAL_SECONDS = 60

logger = logging.getLogger(__name__)


class APIMessenger:
    """
    Sends requests to the API and handles the responses.

    Backlogs requests that failed due to timeout.
    """

    traefik_host_ip: str
    watcher_name: str
    backlog: list[tuple[Action, str]]
    retry_loop_active: bool
    _session: requests.Session
    _api_url: str

    def __init__(self):
        self._api_url = f"{'https' if ENV_CONFIG.HTTPS_ENABLED else 'http'}://{ENV_CONFIG.API_HOST}:{ENV_CONFIG.API_PORT}/api"
        self._session = requests.Session()
        self.traefik_host_ip = get_env("TRAEFIK_HOST_IP")
        self.watcher_name = get_env("WATCHER_NAME")
        self.backlog = []
        self.retry_loop_active = False

    def sync(self, hostnames: list[str]):
        """
        Replaces all current records created by this watcher with a list of new ones.
        """

    def update(self, hostname: str):
        """
        Creates a new record or modifies an existing one.
        """
        logger.info("Sending update")
        try:
            response = self._send_request(
                "POST",
                "/watcher/update",
                json={
                    "record_name": hostname,
                    "content": ENV_CONFIG.TRAEFIK_HOST_IP,
                    "watcher_name": ENV_CONFIG.WATCHER_NAME,
                },
            )
            logger.info(response)
            response.raise_for_status()

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ):
            logger.error("API request timed out")
            self.backlog.append(("UPDATE", hostname))
        except requests.exceptions.HTTPError as exc:
            if exc.response is None:
                return logger.error("API returned an invalid HTTP response", exc)

            try:
                body = exc.response.json()
            except requests.exceptions.JSONDecodeError:
                body = None

            logger.warning("UPDATE operation rejected, API returned %s %s", exc.response.status_code, body)

    def delete(self, hostname: str):
        """
        Moves a record to trash.
        """
        try:
            response = self._send_request(
                "DELETE",
                "/watcher/delete",
                json={
                    "record_name": hostname,
                    "content": ENV_CONFIG.TRAEFIK_HOST_IP,
                    "watcher_name": ENV_CONFIG.WATCHER_NAME,
                },
            )
            response.raise_for_status()

        except requests.exceptions.Timeout, requests.exceptions.ConnectionError:
            self.backlog.append(("DELETE", hostname))
        except requests.exceptions.HTTPError as exc:
            if exc.response is None:
                return logger.error("API returned an invalid HTTP response", exc)
            try:
                body = exc.response.json()
            except requests.exceptions.JSONDecodeError:
                body = None

            logger.warning("DELETE operation rejected, API returned %s %s", exc.response.status_code, body)

    async def start_loop(self):
        if self.retry_loop_active:
            logger.debug("APIMessenger loop is already running - skipping start.")
            return

        self.retry_loop_active = True

        asyncio.create_task(self._retry())

    async def _retry(self):
        """
        Retries failed requests.
        """
        while True:
            if self.backlog:
                ...

            await asyncio.sleep(RETRY_INTERVAL_SECONDS)

    def _send_request(self, method: Literal["POST", "DELETE"], path: str, **kwargs) -> requests.Response:
        logger.info(join_url(self._api_url, path))
        return self._session.request(
            method=method,
            url=join_url(self._api_url, path),
            timeout=5,
            **kwargs,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
