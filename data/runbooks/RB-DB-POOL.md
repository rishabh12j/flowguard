---
document_id: RB-DB-POOL
document_type: runbook
title: Database connection pool exhausted
system: customer-portal
service: account-api
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Database connection pool exhausted

## When to use

Use this runbook when `account-api` times out waiting for a database connection.

## Procedure

1. Check `db_connection_wait_p95_ms` for `account-api` and when it rose.
2. Find the configured pool size in the latest "Connection pool initialised" log and compare it with the capacity in the API contract.
3. If a recent deployment changed the pool size, roll it back, after approval.
4. Confirm the connection wait time drops below 100 ms.

## Warnings

- Restarting `account-api` does not help: the same pool size is read again.
- Do not raise the database's own connection limit. Other services share it.
