import logging
from typing import Literal

import requests

from src.config import API_URL, ENV_CONFIG
from src.utils.paths import join_url

logger = logging.getLogger(__name__)


class APIMessenger:
    """
    Sends requests to the API and handles the responses.
    """

    is_synchronized: bool
    _session: requests.Session

    def __init__(self):
        self._session = requests.Session()
        self.is_synchronized = False

    def sync(self, hostnames: list[str]):
        """
        Replaces all current records created by this watcher with a list of new ones.
        """
        if self._send("SYNC", hostnames):
            self.is_synchronized = True

    def update(self, hostname: str):
        """
        Creates a new record or modifies an existing one.
        """
        self._send("UPDATE", hostname)

    def delete(self, hostname: str):
        """
        Moves a record to trash.
        """
        self._send("DELETE", hostname)

    def _send(self, action: Literal["UPDATE", "DELETE", "SYNC"], data: str | list[str]) -> bool:
        """
        Sends the API request. Returns boolean indicating whether the operation succeded.
        """

        match action:
            case "UPDATE":
                method = "POST"
                path = "/watcher/update"
                data_field_name = "record_name"

            case "DELETE":
                method = "DELETE"
                path = "/watcher/delete"
                data_field_name = "record_name"

            case "SYNC":
                method = "POST"
                path = "/watcher/sync"
                data_field_name = "record_names"

        json = {"content": ENV_CONFIG.TRAEFIK_HOST_IP, data_field_name: data}

        try:
            response = self._session.request(
                method=method,
                url=join_url(API_URL, path),
                timeout=5,
                json=json,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Watcher-Secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                    "X-Watcher-Name": ENV_CONFIG.WATCHER_NAME,
                },
            )
            response.raise_for_status()

            logger.info("%s %s operation succeded", action, str(data))
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ):
            self.is_synchronized = False
            logging.error("%s %s operation failed, API timed out", action, str(data))
            return False

        except requests.exceptions.HTTPError as exc:
            if exc.response is None:
                logger.error("API returned an invalid HTTP response", exc)
                return False

            try:
                body = exc.response.json()

                if not isinstance(body, dict):
                    detail = None

                detail = body.get("detail")
            except requests.exceptions.JSONDecodeError:
                detail = None

            logger.error("%s %s operation rejected, API returned %s - %s", action, str(data), exc.response.status_code, detail)

            if exc.response.status_code >= 500:
                self.is_synchronized = False

            return False
        except Exception:
            logger.exception("Unhandled request exception occured")
            return False

        return True
