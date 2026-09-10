from app.providers.base import DNSProvider


def test_modify_record_name(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"
    new_record_name = f"api.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    modified = provider.modify_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        new_name=new_record_name,
        new_type="A",
        new_content="192.0.2.1",
        new_ttl=300,
    )

    assert modified.name == new_record_name
    assert modified.type == "A"
    assert modified.content == "192.0.2.1"
    assert modified.ttl == 300

    assert (
        provider.get_record(
            zone_name=test_zone,
            name=record_name,
            type_="A",
        )
        is None
    )

    retrieved = provider.get_record(
        zone_name=test_zone,
        name=new_record_name,
        type_="A",
    )

    assert retrieved is not None
    assert retrieved.name == new_record_name


def test_modify_record_type(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    modified = provider.modify_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        new_name=record_name,
        new_type="AAAA",
        new_content="2001:db8::1",
        new_ttl=300,
    )

    assert modified.name == record_name
    assert modified.type == "AAAA"
    assert modified.content == "2001:db8::1"
    assert modified.ttl == 300

    assert (
        provider.get_record(
            zone_name=test_zone,
            name=record_name,
            type_="A",
        )
        is None
    )

    retrieved = provider.get_record(
        zone_name=test_zone,
        name=record_name,
        type_="AAAA",
    )

    assert retrieved is not None
    assert retrieved.type == "AAAA"


def test_modify_record_content(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    modified = provider.modify_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        new_name=record_name,
        new_type="A",
        new_content="192.0.2.42",
        new_ttl=300,
    )

    assert modified.name == record_name
    assert modified.type == "A"
    assert modified.content == "192.0.2.42"
    assert modified.ttl == 300


def test_modify_record_ttl(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    modified = provider.modify_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        new_name=record_name,
        new_type="A",
        new_content="192.0.2.1",
        new_ttl=3600,
    )

    assert modified.name == record_name
    assert modified.type == "A"
    assert modified.content == "192.0.2.1"
    assert modified.ttl == 3600


def test_modify_record_all_fields(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"
    new_record_name = f"mail.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    modified = provider.modify_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        new_name=new_record_name,
        new_type="AAAA",
        new_content="2001:db8::42",
        new_ttl=7200,
    )

    assert modified.name == new_record_name
    assert modified.type == "AAAA"
    assert modified.content == "2001:db8::42"
    assert modified.ttl == 7200

    assert (
        provider.get_record(
            zone_name=test_zone,
            name=record_name,
            type_="A",
        )
        is None
    )

    retrieved = provider.get_record(
        zone_name=test_zone,
        name=new_record_name,
        type_="AAAA",
    )

    assert retrieved is not None
    assert retrieved.name == new_record_name
    assert retrieved.type == "AAAA"
    assert retrieved.content == "2001:db8::42"
    assert retrieved.ttl == 7200


def test_modify_record_without_identity_change(
    provider: DNSProvider,
    test_zone: str,
):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    modified = provider.modify_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        new_name=record_name,
        new_type="A",
        new_content="192.0.2.2",
        new_ttl=600,
    )

    assert modified.name == record_name
    assert modified.type == "A"
    assert modified.content == "192.0.2.2"
    assert modified.ttl == 600

    retrieved = provider.get_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
    )

    assert retrieved is not None
    assert retrieved.content == "192.0.2.2"
    assert retrieved.ttl == 600


def test_delete_record(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    provider.delete_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
    )

    assert (
        provider.get_record(
            zone_name=test_zone,
            name=record_name,
            type_="A",
        )
        is None
    )
