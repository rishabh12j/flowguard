---
document_id: SPEC-INVOICE-V3
document_type: api_spec
title: Invoice ingestion contract
system: invoice-processing
service: invoice-transformer
version: 3.1
effective_date: 2026-06-02
is_current: true
---

# Invoice ingestion contract

Source systems send invoices to `invoice-transformer`, which validates each payload against this contract before forwarding it to `invoice-workflow`.

## POST /v3/invoices

### Headers

| Header | Required | Description |
|---|---|---|
| `X-Correlation-ID` | Yes | Identifier for this processing attempt, passed to every downstream service. |

### Request body

| Field | Type | Required | Description |
|---|---|---|---|
| `supplier_id` | string | Yes | Supplier identifier. |
| `total_amount` | number | Yes | Invoice total. |

Example:

```json
{
  "supplier_id": "SUP-102",
  "total_amount": 1200.50
}
```

Field names are snake_case. Field names and types are matched exactly.

### Validation failure

A payload that does not satisfy this contract raises `SchemaValidationError`. The message is moved to `invoice-transform-dlq` and is not forwarded to `invoice-workflow`.
