# SETUP.MD

## List of contents

### Production

- [Production - Main instance build](#production---main-instance-build)
- [Production - Watcher build](#production---watcher-build)

### Development

- [Development - Main instance build](#development---main-instance-build)
- [Development - Watcher build](#development---watcher-build)

## Production - Main instance build

This section covers building and initializing the **DNS Manager main instance** in production mode. This includes:

- The backend container
- The web app container
- Central watcher instance

### 1. Prepare external dependencies

The application depends on an external PostgreSQL database and running DNS provider. The default configuration in `docker-compose.yml` also requires an external network `dnsnet`, to which the database and DNS provider containers are connected.

If your Docker network has a different name, or your services are running on a separate server, modify `docker-compose.yml` accordingly:

```yml
networks:
    dnsnet:
        external: true
        name: name-of-your-network
```

All deployed DNS Manager containers will connect to this network. This network can therefore be used to reference the external services in your environment variables.

### 2. Configure environment variables

Copy the contents of the `.env.example` to a `.env` file at the project root.

```
cp .env.example .env
```

And replace the placeholders with your configuration.

| Variable                         | Required                   | Description                                                                                                                                                                   | Default (if not set) |
| -------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `DNS_PROVIDER`                   | Yes                        | DNS provider to use. Currently supported: `powerdns`.                                                                                                                         | -                    |
| `POWERDNS_API_URL`               | If `DNS_PROVIDER=powerdns` | URL of the PowerDNS REST API.                                                                                                                                                 | -                    |
| `POWERDNS_API_KEY`               | If `DNS_PROVIDER=powerdns` | Private key used to authenticate with the PowerDNS REST API.                                                                                                                  | -                    |
| `POWERDNS_SERVER_ID`             | If `DNS_PROVIDER=powerdns` | ID of the PowerDNS server to manage.                                                                                                                                          | -                    |
| `DATABASE_URL`                   | Yes                        | Connection URL for the PostgreSQL database.                                                                                                                                   | -                    |
| `AUTHENTICATION_SECRET_KEY`      | Yes                        | Secret key used to sign and verify API access tokens. Should be randomly generated with `openssl rand -hex 32`                                                                | -                    |
| `ADMIN_USERNAME`                 | Yes                        | Username for the application's initial administrator account.                                                                                                                 | -                    |
| `ADMIN_PASSWORD`                 | Yes                        | Password for the application's initial administrator account.                                                                                                                 | -                    |
| `CHECK_INTERVAL_SECONDS`         | No                         | Interval, in seconds, at which the background job checks all active records and provides the frontend with their statuses.                                                    | `300`                |
| `MANAGED_ZONE`                   | No                         | Zone that accepts automatically generated hostnames from the Traefik/Docker watcher. Hostnames outside this zone are ignored and logged. If empty, no hostnames are accepted. | -                    |
| `WATCHER_NAME`                   | Yes                        | Identifier for the watcher instance.                                                                                                                                          | -                    |
| `TRAEFIK_HOST_IP`                | Yes                        | IP address of the Traefik service host.                                                                                                                                       | -                    |
| `LOG_LEVEL`                      | No                         | Backend log level. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                                                                                                  | `INFO`               |
| `ACCESS_TOKEN_LIFETIME_SECONDS`  | No                         | Lifetime of an access token, in seconds.                                                                                                                                      | `3600`               |
| `REFRESH_TOKEN_LIFETIME_SECONDS` | No                         | Lifetime of a refresh token, in seconds.                                                                                                                                      | `259200`             |
| `AUTHENTICATION_ALGORITHM`       | No                         | Algorithm used to sign JWT access tokens.                                                                                                                                     | `HS256`              |
| `HTTPS_ENABLED`                  | No                         | Whether the application is served over HTTPS. If TRUE, authentication cookies will have the Secure attribute set.                                                             | `TRUE`               |

### 3. Build and run the containers

```bash
docker compose up -d --build
```

### 4. Initialize the database

Run the migrations and create the initial administrator. The administrator will only be created if no administrator already exists.

```bash
docker exec dns-manager-backend ./init.sh
```

To create the initial administrator even if an administrator already exists, use the `--force` parameter:

```bash
docker exec dns-manager-backend uv run python -m app.scripts.init_admin --force
```

### 5. Connect to the app

DNS Manager runs at [0.0.0.0:3000](http://0.0.0.0:3000) (available at http://127.0.0.1:3000).

## Production - Watcher build

🚧 WIP 🚧

## Development - Main instance build

### 1. Prepare external dependencies

Follow the same steps as described in the [1. Prepare external dependencies](#1-prepare-external-dependencies) section of the production setup.

### 2. Configure environment variables

Follow the same steps as described in the [2. Configure environment variables](#2-configure-environment-variables) section of the production setup, but define the environment variables in `.env.dev` instead of `.env`:

```
cp .env.example .env.dev
```

### 3. Build and run the containers

```bash
docker compose -f "docker-compose.dev.yml" up -d --build
```

### 4. Initialize the database

Run the migrations and create the initial administrator. The administrator will only be created if no administrator already exists.

```bash
docker exec dns-manager-backend-dev ./init.sh
```

To create the initial administrator even if an administrator already exists, use the `--force` parameter:

```bash
docker exec dns-manager-backend uv run python -m app.scripts.init_admin --force
```

### 5. Connect to the app

DNS Manager runs at [0.0.0.0:3000](http://0.0.0.0:3000) (available at http://127.0.0.1:3000).

API Docs Swagger runs at [0.0.0.0:9000/docs](http://0.0.0.0:9000/docs) (available at http://127.0.0.1:9000/docs).

## Development - Watcher build

🚧 WIP 🚧
