---
document_id: RB-CREDENTIAL-ROTATION
document_type: runbook
title: Rotate the bank API client credential
system: payment-reconciliation
service: settlement-importer
version: 1.4
effective_date: 2026-04-01
is_current: true
---

# Rotate the bank API client credential

## When to use

Use this runbook when `settlement-importer` receives `401 Unauthorized` with `invalid_client` from `bank-api`, or when the credential expiry alert fires.

## Procedure

1. Confirm the expiry date of the current credential in the secrets manager.
2. Request a new client credential through the bank's partner portal.
3. Store the new credential in the secrets manager. Never put it in code, configuration files, or tickets.
4. Send one test request to `bank-api` and confirm it succeeds.
5. Re-run the settlement import for every date that was missed, after approval.

## Warnings

- Do not disable authentication or switch to a shared credential to get the import through.
- Re-running the import before the new credential works only adds more failed attempts.
