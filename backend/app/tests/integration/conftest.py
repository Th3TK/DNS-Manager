import asyncio
from collections.abc import Generator
from uuid import uuid4

import pytest
from app.config import ENV_CONFIG
from app.database.connection import session_factory
from app.main import app
from app.management.dns.record import cleanup_record_metadata
from app.management.dns.zone import cleanup_zone_metadata
from app.management.trash.cleanup import automatic_trash_removal
from app.management.users.users import create_user, delete_user
from app.models.user import CreateUserForm
from app.providers.base import DNSProvider
from app.providers.factory import get_dns_provider
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():

    try:
        yield
    finally:
        automatic_trash_removal.stop()

        with session_factory() as db:
            cleanup_zone_metadata(db)

            if ENV_CONFIG.MANAGED_ZONE:
                cleanup_record_metadata(db, ENV_CONFIG.MANAGED_ZONE)


@pytest.fixture
def provider() -> DNSProvider:
    return get_dns_provider()


@pytest.fixture
def test_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    provider.create_zone(zone_name)

    try:
        yield zone_name
    finally:
        provider.delete_zone(zone_name)


@pytest.fixture
def another_test_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    provider.create_zone(zone_name)

    try:
        yield zone_name
    finally:
        provider.delete_zone(zone_name)


@pytest.fixture
def watcher_managed_zone(provider: DNSProvider):
    zone_name = ENV_CONFIG.MANAGED_ZONE

    if zone_name is None:
        pytest.skip("MANAGED_ZONE is not configured. Skipping watcher tests.")

    zone_exists = provider.get_zone(zone_name) is not None

    if not zone_exists:
        provider.create_zone(zone_name)

    try:
        yield zone_name
    finally:
        if not zone_exists:
            provider.delete_zone(zone_name)


@pytest.fixture
def admin_client() -> Generator[TestClient, None, None]:
    username = f"test-user-{uuid4().hex}@pytest"
    password = uuid4().hex

    with session_factory() as db:
        create_user(
            db,
            CreateUserForm(
                username=username,
                password=password,
                is_admin=True,
            ),
        )

        try:
            response = client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )

            assert response.status_code == 200

            yield client

        finally:
            asyncio.run(delete_user(db, username))
