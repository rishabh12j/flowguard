---
document_id: RB-DNS-RESOLUTION
document_type: runbook
title: A service name can't be resolved
system: ledger-sync
service: ledger-sync
version: 1.0
effective_date: 2026-05-05
is_current: true
---

# A service name can't be resolved

## When to use

Use this runbook when a job fails with "Name or service not known" for an internal name.

## Procedure

1. Check whether the name resolves through `internal-dns`.
2. Look for a recent DNS change, such as a zone migration, and compare its records with the old zone.
3. Roll the DNS change back, after approval, or restore the missing record.
4. Re-run the failed job for the missed day, after approval, once the name resolves.

## Warnings

- Do not put the database's IP address in the job's settings. The database can move.
