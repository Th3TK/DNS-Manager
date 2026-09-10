from app.providers.base import DNSProvider


def test_query_records_exact_name(provider: DNSProvider, test_zone: str):
    name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    provider.create_record(
        zone_name=test_zone,
        name=f"api.{test_zone}",
        type_="A",
        content="192.0.2.2",
        ttl=300,
    )

    records = provider.query_records(name)

    assert len(records) == 1
    assert records[0].name == name
    assert records[0].type == "A"


def test_query_records_exact_name_multiple_types(
    provider: DNSProvider,
    test_zone: str,
):
    name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )
    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="AAAA",
        content="2001:db8::1",
        ttl=600,
    )

    records = provider.query_records(name)

    assert {(record.name, record.type, record.content, record.ttl) for record in records} == {
        (name, "A", "192.0.2.1", 300),
        (name, "AAAA", "2001:db8::1", 600),
    }


def test_query_records_no_match(provider: DNSProvider, test_zone: str):
    provider.create_record(
        zone_name=test_zone,
        name=f"www.{test_zone}",
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    records = provider.query_records(f"api.{test_zone}")

    assert records == []


def test_query_records_star_matches_suffix(
    provider: DNSProvider,
    test_zone: str,
):
    provider.create_record(
        zone_name=test_zone,
        name=f"www.{test_zone}",
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )
    provider.create_record(
        zone_name=test_zone,
        name=f"api.{test_zone}",
        type_="A",
        content="192.0.2.2",
        ttl=300,
    )
    provider.create_record(
        zone_name=test_zone,
        name=f"mail.{test_zone}",
        type_="A",
        content="192.0.2.3",
        ttl=300,
    )

    records = provider.query_records(f"*.{test_zone}")

    assert {record.name for record in records} == {
        f"www.{test_zone}",
        f"api.{test_zone}",
        f"mail.{test_zone}",
    }


def test_query_records_star_matches_prefix(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"www.{test_zone}",
        f"www2.{test_zone}",
        f"www-test.{test_zone}",
        f"api.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records(f"www*.{test_zone}")

    assert {record.name for record in records} == {
        f"www.{test_zone}",
        f"www2.{test_zone}",
        f"www-test.{test_zone}",
    }


def test_query_records_star_matches_middle(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"api.{test_zone}",
        f"api-v2.{test_zone}",
        f"api-prod.{test_zone}",
        f"api-test-prod.{test_zone}",
        f"www.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records(f"api*prod.{test_zone}")

    assert {record.name for record in records} == {
        f"api-prod.{test_zone}",
        f"api-test-prod.{test_zone}",
    }


def test_query_records_star_matches_zero_characters(
    provider: DNSProvider,
    test_zone: str,
):
    name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    records = provider.query_records(f"www*.{test_zone}")

    assert len(records) == 1
    assert records[0].name == name


def test_query_records_question_mark_matches_one_character(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"api1.{test_zone}",
        f"api2.{test_zone}",
        f"api10.{test_zone}",
        f"api.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records(f"api?.{test_zone}")

    assert {record.name for record in records} == {
        f"api1.{test_zone}",
        f"api2.{test_zone}",
    }


def test_query_records_question_mark_does_not_match_zero_characters(
    provider: DNSProvider,
    test_zone: str,
):
    provider.create_record(
        zone_name=test_zone,
        name=f"api.{test_zone}",
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    records = provider.query_records(f"api?.{test_zone}")

    assert records == []


def test_query_records_question_mark_does_not_match_multiple_characters(
    provider: DNSProvider,
    test_zone: str,
):
    provider.create_record(
        zone_name=test_zone,
        name=f"api123.{test_zone}",
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    records = provider.query_records(f"api?.{test_zone}")

    assert records == []


def test_query_records_multiple_question_marks(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"api01.{test_zone}",
        f"api12.{test_zone}",
        f"api1.{test_zone}",
        f"api123.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records(f"api??.{test_zone}")

    assert {record.name for record in records} == {
        f"api01.{test_zone}",
        f"api12.{test_zone}",
    }


def test_query_records_combined_wildcards(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"api1-prod.{test_zone}",
        f"api2-prod.{test_zone}",
        f"api10-prod.{test_zone}",
        f"api1-test.{test_zone}",
        f"www-prod.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records(f"api?-*prod.{test_zone}")

    assert {record.name for record in records} == {
        f"api1-prod.{test_zone}",
        f"api2-prod.{test_zone}",
    }


def test_query_records_star_matches_across_labels(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"api.{test_zone}",
        f"api.v1.{test_zone}",
        f"api.prod.v1.{test_zone}",
        f"www.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records(f"api*.{test_zone}")

    assert {record.name for record in records} == {
        f"api.{test_zone}",
        f"api.v1.{test_zone}",
        f"api.prod.v1.{test_zone}",
    }


def test_query_records_across_zones(
    provider: DNSProvider,
    test_zone: str,
    another_test_zone: str,
):
    name_1 = f"www.{test_zone}"
    name_2 = f"www.{another_test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name_1,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )
    provider.create_record(
        zone_name=another_test_zone,
        name=name_2,
        type_="A",
        content="192.0.2.2",
        ttl=300,
    )

    records = provider.query_records("www.*")

    assert {record.name for record in records} == {
        name_1,
        name_2,
    }


def test_query_records_matches_multiple_types_across_zones(
    provider: DNSProvider,
    test_zone: str,
    another_test_zone: str,
):
    name_1 = f"www.{test_zone}"
    name_2 = f"www.{another_test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name_1,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )
    provider.create_record(
        zone_name=test_zone,
        name=name_1,
        type_="AAAA",
        content="2001:db8::1",
        ttl=600,
    )
    provider.create_record(
        zone_name=another_test_zone,
        name=name_2,
        type_="A",
        content="192.0.2.2",
        ttl=300,
    )

    records = provider.query_records("www.*")

    assert {(record.name, record.type, record.content) for record in records} == {
        (name_1, "A", "192.0.2.1"),
        (name_1, "AAAA", "2001:db8::1"),
        (name_2, "A", "192.0.2.2"),
    }


def test_query_records_star_only(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"www.{test_zone}",
        f"api.{test_zone}",
        f"mail.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records("*")

    returned_names = {record.name for record in records}

    assert returned_names >= set(names)


def test_query_records_question_mark_in_middle(
    provider: DNSProvider,
    test_zone: str,
):
    names = [
        f"web1.example.{test_zone}",
        f"web2.example.{test_zone}",
        f"web10.example.{test_zone}",
        f"web1.test.{test_zone}",
    ]

    for index, name in enumerate(names, start=1):
        provider.create_record(
            zone_name=test_zone,
            name=name,
            type_="A",
            content=f"192.0.2.{index}",
            ttl=300,
        )

    records = provider.query_records(f"web?.example.{test_zone}")

    assert {record.name for record in records} == {
        f"web1.example.{test_zone}",
        f"web2.example.{test_zone}",
    }


def test_query_records_preserves_record_properties(
    provider: DNSProvider,
    test_zone: str,
):
    name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="A",
        content="192.0.2.123",
        ttl=1234,
    )

    records = provider.query_records(name)

    assert len(records) == 1

    record = records[0]
    assert record.name == name
    assert record.type == "A"
    assert record.content == "192.0.2.123"
    assert record.ttl == 1234


def test_query_records_star_returns_all_records_across_zones(
    provider: DNSProvider,
    test_zone: str,
    another_test_zone: str,
):
    www_1 = f"www.{test_zone}"
    api_1 = f"api.{test_zone}"
    www_2 = f"www.{another_test_zone}"
    mail_2 = f"mail.{another_test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=www_1,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )
    provider.create_record(
        zone_name=test_zone,
        name=api_1,
        type_="A",
        content="192.0.2.2",
        ttl=300,
    )
    provider.create_record(
        zone_name=another_test_zone,
        name=www_2,
        type_="AAAA",
        content="2001:db8::1",
        ttl=600,
    )
    provider.create_record(
        zone_name=another_test_zone,
        name=mail_2,
        type_="MX",
        content="10 mail.example.com.",
        ttl=900,
    )

    records = provider.query_records("*")

    assert {(record.name, record.type) for record in records} >= {
        (www_1, "A"),
        (api_1, "A"),
        (www_2, "AAAA"),
        (mail_2, "MX"),
    }
