# Expanding the application

The application is designed to be easily expanded to support new DNS providers through creation of custom adapters. This document is meant to be a guide for that very purpose.

## Abstraction layer

All communication with the DNS providers goes through an abstraction layer located in the `/backend/app/providers` package. The directory contains:

- `base.py` - a base Python `Protocol` for creating provider adapters.
- `factory.py` - creates a `provider` instance based on the environmental variable DNS_PROVIDER.
- directories containing implementations of adapters for DNS providers.

The rest of the application only imports the provider instance from `factory.py`. Provider-specific adapters are not imported directly elsewhere in the application.

## Creating a new adapter

### 1. Prepare the environment

In the file `/backend/app/config.py` find a line that declares the `DNS_PROVIDER` environment variable. It should look like this:

```py
@dataclass(frozen=True)
class EnvConfig:
    ...
    DNS_PROVIDER: str = get_env_literal("DNS_PROVIDER", {"powerdns"})
    ...
```

Expand the allowed values with `<your-provider-name>`, like this:

```py
DNS_PROVIDER: str = get_env_literal("DNS_PROVIDER", {"powerdns" "<your-provider-name>"})
```

Now expand the dataclass by adding environment variables required for your provider. For example:

```py
@dataclass(frozen=True)
class EnvConfig:
    ...
    DNS_PROVIDER: str = get_env_literal("DNS_PROVIDER", {"powerdns" "<your-provider-name>"})
    ...
    YOUR_PROVIDER_API_URL: str = get_env("YOUR_PROVIDER_API_URL", default="", accept_empty=True)
    YOUR_PROVIDER_API_KEY: str = get_env("YOUR_PROVIDER_API_KEY", default="", accept_empty=True)
    ...
```

Ensure they all have a set default value and accept empty values. Otherwise they will be required by the application even when `DNS_PROVIDER` is set to another provider. You may also use `get_env_int` for integer variables or `get_env_literal` for a variable that accepts strings from a list of options.

### 2. Create the adapter

In the `/backend/app/providers` package create a new directory `/<your-provider-name>`. Inside that directory create files `adapter.py` and `models.py`. `adapter.py` will hold the logic while `models.py` will define models used in the direct requests with your provider.

In `adapter.py`, create a class named `YourProviderNameAdapter` that implements the `DNSProvider` Protocol defined in `base.py`.

The adapter is responsible for translation between application models and the DNS provider. It must implement every method defined by the `DNSProvider`.

#### 2.1 Prerequisites

The following checks are performed before any request reaches the adapter:

- Duplicate and existing-resource checks are performed beforehand.
- Field types and length limits are validated beforehand.
- General DNS rules are validated beforehand.
- DNS syntax is validated beforehand. The API allows alphanumeric characters, hyphens and underscores in the DNS names. If the provider has sticter requirements, further validation should be handled by the adapter.

#### 2.2 Requirements

- All methods must return the types specified by the DNSProvider protocol.
- Raised exceptions must be of type `HTTPException` imported from `fastapi`.
- Provider unreachable should raise `HTTP 503` with an appropriate detail.
- Provider internal errors should raise `HTTP 502` with an appropriate detail.
- Provider authentication errors should raise `HTTP 503` with an appropriate detail.
- Client errors should raise appropriate `HTTP 4XX` status.

#### 2.3 Return models

Adapter methods have following return models:

`DNSZoneProperties` imported from `app.models.zone`

> Zones are identified by name and queried using it.

`DNSRecordProperties` imported from `app.models.record`

> Records are identified by (zone_name, name, type). The application does not allow creating multiple records with the same key. DNSRecordProperties normally represents a single record. If the provider contains multiple records with the same key due to external creation, content must contain a `list[str]` with all record contents.

#### 2.4 Method requirements

Method requirements are documented as docstrings in the `DNSProvider` protocol.

### 3. Register the Adapter in the Factory

Lastly, in `factory.py`, add your provider to `get_dns_provider()` function:

```py
def get_dns_provider() -> DNSProvider:
    match ENV_CONFIG.DNS_PROVIDER:
        ...
        case "your-provider-name"
            return YourProviderNameDNSAdapter()
        ...
```
