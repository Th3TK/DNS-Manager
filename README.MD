# DNS Manager

A easy-to-use web application for managing your DNS server combined with a watcher service automatically generating records for Docker containers with Traefik hostnames.

## Features

- User friendly interface for managing DNS zones and records.
- Watcher service with automatic creation/removal of `A` records pointing to the Traefik proxy based on Docker containers state and configuration.
- Support for remote watchers installed on other servers.
- Dashboard displaying resolution and reachability statuses of `A`, `AAAA` and `CNAME` records.
- Integrated change history for user action logging.
- Viewer accounts with read-only permissions.
- Verbose error handling and input validation.
- DNS provider status display.
- Soft-delete system keeping deleted objects for 30 days before permanent deletion.

## Currently supported DNS providers

- PowerDNS

## Instalation & requirements

Installation guide is available at [SETUP.md](./docs/SETUP.md).

## More about the project

### Watcher service

The watcher service automatically manages records for containers configured to run behind a Traefik proxy. One central watcher runs in the DNS manager main instance. Further watchers may be installed on other servers and reach the DNS manager backend remotely.

#### Container start

When a Docker container starts, the watcher reads `traefik.http.routers.<name>.rule` labels and creates `A` records for all `Host` values. The records point to `TRAEFIK_IP` set in the watcher instance environment configuration. Set hostnames must be within a `MANAGED_ZONE`, set in the DNS manager backend configuration, otherwise they will be rejected by the backend API.

**Override behavior**

- If there is already a matching record with identical content, update will be skipped. Record will retain its origin and metadata.`
- If a record with matching name and type already exists, it will be overriden by the watcher. Record origin will be changed to `automatic => traefik` and author to `watcher:<WATCHER_NAME>`.
- If there is no active matching record, but it exists in the trash, it will be restored.
- Otherwise, a new record will get created.

#### Container shutdown

When a container stops (Docker event `die`), defined automatic records will be moved to trash. Matching manual/external records with identical content will not be affected.

#### Synchronization

If the watcher or the DNS Manager API is inactive during the creation or stopping of containers, the state will be reconciled as soon as both services are running again.
