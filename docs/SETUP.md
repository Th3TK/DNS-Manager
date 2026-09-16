# SETUP.MD

## List of contents

### Production

- [Production - Main instance build](#production---main-instance-build)
- [Production - Watcher build](#production---watcher-build)

### Development

- [Development - Main instance build](#development)

<br>

## Production - Main instance build

This section covers building and initializing the **DNS Manager main instance** in production mode. This includes:

- The backend container
- The web app container
- Central watcher instance

### 1. Prepare external dependencies

The application depends on an external PostgreSQL database and running DNS provider. The default configuration in `docker-compose.yml` also requires an external network `dnsnet`, to which the database and DNS provider containers are connected.

If your Docker network has a different name, or your services are running on a separate server, modify `docker-compose.yml` accordingly.

All deployed DNS Manager containers will connect to this network. This network can therefore be used to reference the external services in your environment variables.

### 2. Configure environment variables

Copy the contents of the `.env.example` to a `.env` file at the project root.

```
cp .env.example .env
```

And replace the placeholders with your configuration.

| Variable                         | Required                   | Description                                                                                                                                                                                                                 | Default (if not set) |
| -------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `DNS_PROVIDER`                   | Yes                        | DNS provider to use. Currently supported: `powerdns`.                                                                                                                                                                       | -                    |
| `DNS_RESOLVER`                   | Yes                        | Hostname or address and port (default: 53) of the DNS resolver used for DNS resolution checks.                                                                                                                              | -                    |
| `POWERDNS_API_URL`               | If `DNS_PROVIDER=powerdns` | URL of the PowerDNS REST API.                                                                                                                                                                                               | -                    |
| `POWERDNS_API_KEY`               | If `DNS_PROVIDER=powerdns` | Private key used to authenticate with the PowerDNS REST API.                                                                                                                                                                | -                    |
| `POWERDNS_SERVER_ID`             | If `DNS_PROVIDER=powerdns` | ID of the PowerDNS server to manage.                                                                                                                                                                                        | -                    |
| `DATABASE_URL`                   | Yes                        | Connection URL for the PostgreSQL database.                                                                                                                                                                                 | -                    |
| `AUTH_SECRET_KEY`                | Yes                        | Secret key used to sign and verify API access tokens. Should be randomly generated with `openssl rand -hex 32`                                                                                                              | -                    |
| `WATCHER_AUTH_SECRET_KEY`        | Yes                        | Secret key used to verify API requests sent by the watcher. Should be randomly generated with `openssl rand -hex 32`                                                                                                        | -                    |
| `ADMIN_USERNAME`                 | Yes                        | Username for the application's initial administrator account. Username must be between 3 and 64 characters in length (inclusive), and only contain lowercase letters, digits, and the following characters: \_ @ . + : $ -. | -                    |
| `ADMIN_PASSWORD`                 | Yes                        | Password for the application's initial administrator account.                                                                                                                                                               | -                    |
| `API_PORT`                       | No                         | Port on which the API will be exposed.                                                                                                                                                                                      | `9000`               |
| `FRONTEND_PORT`                  | No                         | Port on which the web application will be exposed.                                                                                                                                                                          | `3000`               |
| `HTTPS_ENABLED`                  | No                         | Whether the components should communicate over HTTPS (and WSS). If `TRUE`, authentication cookies will have the Secure attribute set.                                                                                       | `FALSE`              |
| `CHECK_INTERVAL_SECONDS`         | No                         | Interval, in seconds, at which the background job checks all active records and provides the frontend with their statuses.                                                                                                  | `300`                |
| `MANAGED_ZONE`                   | No                         | Zone that accepts automatically generated hostnames from the Traefik/Docker watcher. Hostnames outside this zone are ignored and logged. If empty, no hostnames are accepted.                                               | -                    |
| `WATCHER_NAME`                   | Yes                        | Identifier for the central watcher instance. Should be unique among other watchers and not exceed 56 characters in length. Duplicate names may cause undefined behavior.                                                    | -                    |
| `TRAEFIK_HOST_IP`                | Yes                        | IP address of the Traefik service host. Must be a [valid IPv4 address](https://docs.python.org/3/library/ipaddress.html#:~:text=address%2E-,The,first%29%2E) otherwise the watcher instance will fail.                      | -                    |
| `LOG_LEVEL`                      | No                         | Backend log level. Applies to the central watcher container as well. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                                                                                              | `INFO`               |
| `ACCESS_TOKEN_LIFETIME_SECONDS`  | No                         | Lifetime of an access token, in seconds.                                                                                                                                                                                    | `3600`               |
| `REFRESH_TOKEN_LIFETIME_SECONDS` | No                         | Lifetime of a refresh token, in seconds.                                                                                                                                                                                    | `259200`             |

If any of the required environmental variables are not configured, the backend will fail with a `ValueError`.

### 3. Build and run the containers

On backend startup, database migrations are applied automatically and the initial administrator account is created.

```bash
docker compose up -d --build
```

### 4. Verify containers

Check the container logs to verify that the application components start successfully and are running correctly.

### 5. Connect to the app

DNS Manager web application runs by default at [0.0.0.0:3000](http://0.0.0.0:3000) (available at http://127.0.0.1:3000).

<br>

## Production - Watcher build

This section covers building and initializing a **Remote Watcher** in production mode. This watcher instance is intended to run on a seperate server and communicate with the API remotely.

### 1. Configure environment variables

Copy the contents of the `.env.watcher.example` to a `.env` file at the project root.

```
cp .env.watcher.example .env
```

And replace the placeholders with your configuration.

| Variable                  | Required | Description                                                                                                                                                                                            | Default (if not set) |
| ------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------- |
| `API_URL`                 | Yes      | URL used to reach the DNS Manager API.                                                                                                                                                                 | -                    |
| `WATCHER_AUTH_SECRET_KEY` | Yes      | Secret key used to verify API requests sent by the watcher. Must match the secret key specified in the main DNS Manager instance, otherwise all API requests will raise HTTP 401                       | -                    |
| `WATCHER_NAME`            | Yes      | Identificator of the watcher instance. Should be unique among other watchers and not exceed 56 characters in length. Duplicate names may cause undefined behavior.                                     | -                    |
| `TRAEFIK_HOST_IP`         | Yes      | IP address of the Traefik service host. Must be a [valid IPv4 address](https://docs.python.org/3/library/ipaddress.html#:~:text=address%2E-,The,first%29%2E) otherwise the watcher instance will fail. | -                    |
| `LOG_LEVEL`               | No       | Container log level. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                                                                                                                         | `INFO`               |

If any of the required environmental variables are not configured, the watcher application will fail with a `ValueError`.

### 2. Build and run the container

```bash
docker compose -f "docker-compose.watcher.yml" up -d --build
```

### 3. Verify watcher

Check the container logs to verify that the watcher starts successfully and is running correctly.

#### Connection errors

On startup, the watcher will attempt to synchronize the API configuration with the current container state.

- If the API returns `401`, verify if your `WATCHER_AUTH_SECRET_KEY` matches the secret key specified in the main DNS manager instance.

<br>

## Development

Follow the same steps as described in the [production setup](#production---main-instance-build), but use the `docker-compose.dev.yml` compose file during build:

```bash
docker compose -f "docker-compose.dev.yml" up -d --build
```
