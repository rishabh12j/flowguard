---
document_id: SPEC-ACCOUNT-API-V1
document_type: api_spec
title: Account API
system: customer-portal
service: account-api
version: 1.8
effective_date: 2026-05-01
is_current: true
---

# Account API

`web-frontend` calls `account-api` to show each customer's account page, and `account-api` reads from `accounts-db`.

## Performance

`GET /v1/accounts/{id}` answers within 500 ms at the 95th percentile. `web-frontend` waits at most 5 seconds and then returns `504 Gateway Timeout`.

## Capacity

At the morning peak, `account-api` uses about 40 database connections at once, so its connection pool is sized at 50. A smaller pool makes requests queue for a connection, and a request that waits 30 seconds fails.
