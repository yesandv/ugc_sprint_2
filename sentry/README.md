# Sentry Setup

### Start containers
```shell
docker compose up -d
```

### Apply migrations and create a user:
```shell
docker compose exec sentry-api sentry upgrade
```
