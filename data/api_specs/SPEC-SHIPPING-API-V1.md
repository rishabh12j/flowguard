---
document_id: SPEC-SHIPPING-API-V1
document_type: api_spec
title: Carrier shipping API
system: order-fulfilment
service: shipping-api
version: 1.6
effective_date: 2026-02-01
is_current: true
---

# Carrier shipping API

`order-sync-worker` creates one shipment for each order, and the carrier returns a shipping label.

## Rate limits

Each client may send at most 100 requests per minute. A client over the limit receives `429 Too Many Requests` with a `Retry-After` header, in seconds. Clients must wait at least that long before retrying. Retrying sooner extends the block.

## POST /v1/shipments

Creates a shipment and returns its label. The body needs the order ID, the delivery address, and the parcel weight. A successful request returns `201 Created`.
