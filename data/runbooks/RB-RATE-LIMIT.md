---
document_id: RB-RATE-LIMIT
document_type: runbook
title: Carrier API rate limiting
system: order-fulfilment
service: order-sync-worker
version: 2.0
effective_date: 2026-05-15
is_current: true
---

# Carrier API rate limiting

## When to use

Use this runbook when `order-sync-worker` receives `429 Too Many Requests` from `shipping-api`.

## Procedure

1. Check the `outbound_requests_per_minute` metric for `order-sync-worker` and find when it went above 100.
2. Find the source of the extra traffic. Backfills and bulk imports are the usual cause.
3. Pause the job that is sending the extra traffic, after approval.
4. Limit `order-sync-worker` to 90 requests per minute, so normal traffic stays within the quota.
5. Retry the failed shipments once the rate is below the limit.

## Warnings

- Do not retry failed shipments immediately: retrying inside the block extends it.
- Do not disable the carrier integration. Orders would stop shipping entirely.
