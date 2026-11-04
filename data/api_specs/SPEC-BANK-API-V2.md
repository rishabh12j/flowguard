---
document_id: SPEC-BANK-API-V2
document_type: api_spec
title: Bank settlement API
system: payment-reconciliation
service: bank-api
version: 2.0
effective_date: 2026-01-10
is_current: true
---

# Bank settlement API

The bank provides one settlement file per business day. `settlement-importer` downloads it each morning at 06:00 UTC.

## Authentication

Clients authenticate with a client credential issued by the bank. Each client credential is valid for 90 days from issue and stops working at its expiry time. A request with an expired client credential is rejected with `401 Unauthorized` and the error code `invalid_client`. Retrying does not help: only a new client credential, issued through the bank's partner portal, restores access.

## GET /v2/settlements

Returns the settlement lines for one business day. The `date` query parameter is required and uses the format `YYYY-MM-DD`. A day with no settlements returns an empty list, not an error.
