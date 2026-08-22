# Running Tests

## 1. Setting up a testing environment

Build the development environment by following the [setup guide](SETUP.md#development---main-instance-build).

Ensure that `DATABASE_URL` points to a test database rather than the production database.

Ensure that the DNS provider configuration points to a test server rather than the production server. For example, when using PowerDNS, set `POWERDNS_SERVER_ID` to a test server.

Some tests directly modify the DNS provider's configuration. Although the tests are designed to avoid affecting unrelated configuration, running them against a production server is unsafe and should be avoided.

## 2. Run tests

```bash
docker exec dns-manager-backend-dev ./runtests.sh
```
