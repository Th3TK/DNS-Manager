"""
Tests POST /watcher/sync endpoint.

Ensures watcher sync action works properly.
"""

from uuid import uuid4

from app.config import ENV_CONFIG
from app.models.record import DNSRecord
from app.providers.factory import provider
from fastapi.testclient import TestClient


def test_sync_ignore_manual_not_included(watcher_managed_zone: str, admin_client: TestClient):
    hostname = f"{uuid4().hex}.{watcher_managed_zone}"
    watcher_name = f"test-watcher-{uuid4()}"
    ip = "1.1.1.1"

    try:
        response = admin_client.post(
            f"/zones/{watcher_managed_zone}/record",
            json={
                "name": hostname,
                "type": "A",
                "content": ip,
                "ttl": 3600,
                "comment": "Manual equal",
                "checks_enabled": True,
            },
        )

        assert response.status_code == 201

        response = admin_client.post(
            "/watcher/sync",
            json={
                "record_names": [],
                "content": ip,
            },
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name,
            },
        )

        assert response.status_code == 204

        response = admin_client.get(f"/zones/{watcher_managed_zone}/records")

        assert response.status_code == 200

        records = response.json()

        assert records

        record = DNSRecord.model_validate(
            next(
                (record for record in records if record["name"] == hostname and record["type"] == "A"),
                None,
            )
        )

        assert record is not None
        assert record.name == hostname
        assert record.type == "A"
        assert record.content == ip
        assert record.author is not None
        assert not record.author.startswith("watcher")
        assert record.author != f"watcher:{watcher_name}"
        assert record.origin == "manual"
        assert record.checks_enabled
        assert record.comment == "Manual equal"
        assert record.ttl == 3600

    finally:
        provider.delete_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
        )


def test_sync_ignore_manual_equal(watcher_managed_zone: str, admin_client: TestClient):
    hostname = f"{uuid4().hex}.{watcher_managed_zone}"
    watcher_name = f"test-watcher-{uuid4()}"
    ip = "1.1.1.1"

    try:
        response = admin_client.post(
            f"/zones/{watcher_managed_zone}/record",
            json={
                "name": hostname,
                "type": "A",
                "content": ip,
                "ttl": 3600,
                "comment": "Manual equal",
                "checks_enabled": True,
            },
        )

        assert response.status_code == 201

        response = admin_client.post(
            "/watcher/sync",
            json={
                "record_names": [hostname],
                "content": ip,
            },
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name,
            },
        )

        assert response.status_code == 204

        response = admin_client.get(f"/zones/{watcher_managed_zone}/records")

        assert response.status_code == 200

        records = response.json()

        assert records

        record = DNSRecord.model_validate(
            next(
                (record for record in records if record["name"] == hostname and record["type"] == "A"),
                None,
            )
        )

        assert record is not None
        assert record.name == hostname
        assert record.type == "A"
        assert record.content == ip
        assert record.author is not None
        assert not record.author.startswith("watcher")
        assert record.author != f"watcher:{watcher_name}"
        assert record.origin == "manual"
        assert record.checks_enabled
        assert record.comment == "Manual equal"
        assert record.ttl == 3600

    finally:
        provider.delete_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
        )


def test_sync_override_manual(watcher_managed_zone: str, admin_client: TestClient):
    hostname = f"{uuid4().hex}.{watcher_managed_zone}"
    watcher_name = f"test-watcher-{uuid4()}"
    ip_1 = "1.1.1.1"
    ip_2 = "2.2.2.2"

    try:
        response = admin_client.post(
            f"/zones/{watcher_managed_zone}/record",
            json={
                "name": hostname,
                "type": "A",
                "content": ip_1,
                "ttl": 3600,
                "comment": "Manual equal",
                "checks_enabled": True,
            },
        )

        assert response.status_code == 201

        response = admin_client.post(
            "/watcher/sync",
            json={
                "record_names": [hostname],
                "content": ip_2,
            },
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name,
            },
        )

        assert response.status_code == 204

        response = admin_client.get(f"/zones/{watcher_managed_zone}/records")

        assert response.status_code == 200

        records = response.json()

        assert records

        record = DNSRecord.model_validate(
            next(
                (record for record in records if record["name"] == hostname and record["type"] == "A"),
                None,
            )
        )

        assert record is not None
        assert record.name == hostname
        assert record.type == "A"
        assert record.content == ip_2
        assert record.author == f"watcher:{watcher_name}"
        assert record.origin == "automatic => traefik"
        assert record.checks_enabled
        assert not record.comment
        assert record.ttl == 60

    finally:
        provider.delete_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
        )


def test_sync_override_external(watcher_managed_zone: str, admin_client: TestClient):
    hostname = f"{uuid4().hex}.{watcher_managed_zone}"
    watcher_name = f"test-watcher-{uuid4()}"
    ip_1 = "1.1.1.1"
    ip_2 = "2.2.2.2"

    try:
        provider.create_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
            content=ip_1,
            ttl=3600,
        )

        response = admin_client.post(
            "/watcher/sync",
            json={
                "record_names": [hostname],
                "content": ip_2,
            },
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name,
            },
        )

        assert response.status_code == 204

        response = admin_client.get(f"/zones/{watcher_managed_zone}/records")

        assert response.status_code == 200

        records = response.json()

        assert records

        record = DNSRecord.model_validate(
            next(
                (record for record in records if record["name"] == hostname and record["type"] == "A"),
                None,
            )
        )

        assert record is not None
        assert record.name == hostname
        assert record.type == "A"
        assert record.content == ip_2
        assert record.author == f"watcher:{watcher_name}"
        assert record.origin == "automatic => traefik"
        assert record.checks_enabled
        assert not record.comment
        assert record.ttl == 60

    finally:
        provider.delete_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
        )


def test_sync_override_automatic(watcher_managed_zone: str, admin_client: TestClient):
    hostname = f"{uuid4().hex}.{watcher_managed_zone}"
    watcher_name_1 = f"test-watcher-{uuid4()}"
    watcher_name_2 = f"test-watcher-{uuid4()}"
    ip_1 = "1.1.1.1"
    ip_2 = "2.2.2.2"

    try:
        response = admin_client.post(
            f"/watcher/update?record_name={hostname}&content={ip_1}",
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name_1,
            },
        )

        assert response.status_code == 204

        response = admin_client.post(
            "/watcher/sync",
            json={
                "record_names": [hostname],
                "content": ip_2,
            },
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name_2,
            },
        )

        assert response.status_code == 204

        response = admin_client.get(f"/zones/{watcher_managed_zone}/records")

        assert response.status_code == 200

        records = response.json()

        assert records

        record = DNSRecord.model_validate(
            next(
                (record for record in records if record["name"] == hostname and record["type"] == "A"),
                None,
            )
        )

        assert record is not None
        assert record.name == hostname
        assert record.type == "A"
        assert record.content == ip_2
        assert record.author == f"watcher:{watcher_name_2}"
        assert record.origin == "automatic => traefik"
        assert record.checks_enabled
        assert not record.comment
        assert record.ttl == 60

    finally:
        provider.delete_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
        )


def test_sync_ignore_records_from_other_watchers_when_deleting(watcher_managed_zone: str, admin_client: TestClient):
    hostname = f"{uuid4().hex}.{watcher_managed_zone}"
    watcher_name_1 = f"test-watcher-{uuid4()}"
    watcher_name_2 = f"test-watcher-{uuid4()}"
    ip_1 = "1.1.1.1"
    ip_2 = "2.2.2.2"

    try:
        response = admin_client.post(
            f"/watcher/update?record_name={hostname}&content={ip_1}",
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name_1,
            },
        )

        assert response.status_code == 204

        response = admin_client.post(
            "/watcher/sync",
            json={
                "record_names": [],
                "content": ip_2,
            },
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name_2,
            },
        )

        assert response.status_code == 204

        response = admin_client.get(f"/zones/{watcher_managed_zone}/records")

        assert response.status_code == 200

        records = response.json()

        assert records

        record = DNSRecord.model_validate(
            next(
                (record for record in records if record["name"] == hostname and record["type"] == "A"),
                None,
            )
        )

        assert record is not None
        assert record.name == hostname
        assert record.type == "A"
        assert record.content == ip_1
        assert record.author == f"watcher:{watcher_name_1}"
        assert record.origin == "automatic => traefik"
        assert record.checks_enabled
        assert not record.comment
        assert record.ttl == 60

    finally:
        provider.delete_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
        )


def test_sync_delete_old_records_same_watcher(watcher_managed_zone: str, admin_client: TestClient):
    hostname = f"{uuid4().hex}.{watcher_managed_zone}"
    watcher_name = f"test-watcher-{uuid4()}"
    ip = "1.1.1.1"

    try:
        response = admin_client.post(
            f"/watcher/update?record_name={hostname}&content={ip}",
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name,
            },
        )

        assert response.status_code == 204

        response = admin_client.post(
            "/watcher/sync",
            json={
                "record_names": [],
                "content": ip,
            },
            headers={
                "x-watcher-secret": ENV_CONFIG.WATCHER_AUTH_SECRET_KEY,
                "x-watcher-name": watcher_name,
            },
        )

        assert response.status_code == 204

        response = admin_client.get(f"/zones/{watcher_managed_zone}/records")

        assert response.status_code == 200

        records = response.json()

        record = next(
            (record for record in records if record["name"] == hostname and record["type"] == "A"),
            None,
        )

        assert record is None

    finally:
        provider.delete_record(
            zone_name=watcher_managed_zone,
            name=hostname,
            type_="A",
        )
