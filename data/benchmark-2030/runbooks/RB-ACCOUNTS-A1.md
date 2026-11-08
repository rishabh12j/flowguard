---
document_id: RB-ACCOUNTS-A1
document_type: runbook
title: Rotate the accounts-partner-api client credential
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Rotate the accounts-partner-api client credential

## When to use

Use this runbook when accounts-worker receives 401 Unauthorized from accounts-partner-api.

## Procedure

1. Confirm the credential's expiry date in the secrets manager.
2. Issue a new credential through the provider's portal and store it in the secrets manager.
3. Resend the failed work, after approval.

## Warnings

- Never put a credential in code or configuration files.
