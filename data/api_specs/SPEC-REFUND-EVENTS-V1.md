---
document_id: SPEC-REFUND-EVENTS-V1
document_type: api_spec
title: Refund events
system: refunds
service: message-broker
version: 1.0
effective_date: 2026-02-01
is_current: true
---

# Refund events

`refund-api` publishes one event per approved refund, and `refund-worker` consumes them and pays the refund through `payment-gateway`.

## Delivery

Delivery is at least once. A consumer commits its offset after processing. After a broker failover or a consumer restart, every event after the last committed offset is delivered again, so a consumer must recognise an event it has already processed, keyed on `refund_id`.

## Event fields

Each event carries `refund_id`, `order_id`, `amount`, and `currency`. `refund_id` is unique per refund.
