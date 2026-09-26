# IP, idea use and collaboration model

## Product behavior

The application is designed so that:

1. Public viewing is separate from permission to use.
2. Permission-required ideas expose only a deliberately selected high-level subset through public endpoints.
3. A requester can submit identity, organization, role, professional profile, purpose and requested rights.
4. The requester must accept the exact current agreement version and type a signature matching the submitted name.
5. The backend stores the agreement version and SHA-256 hash with the request.
6. The owner can approve, reject/revoke, or request more information.
7. Approval creates a separate PermissionGrant record.
8. The owner may issue a time-limited bearer URL for restricted idea details; the raw token is never stored in the database, only its HMAC/sha256-derived hash.
9. The owner can revoke that access link independently.
10. Administrative actions are written to the audit log.
11. Restricted links enforce the approved rights scope; access to an implementation field is not granted merely because a requester asked for it.

## Legal wording boundary

Do not state that every abstract idea is automatically protected or that every independent implementation is automatically unlawful. Protection depends on the kind of material and applicable law. This product therefore focuses on controlled disclosure, explicit permission, confidentiality records and contracts rather than a blanket claim over all abstract ideas.

The agreement templates in the product are implementation templates. They should be reviewed and adapted by qualified counsel before being relied upon for patents, confidential disclosures, licenses, commercial development or disputes.

## Restricted link warning

A restricted access URL functions as a bearer credential. The owner should transmit it only to the intended approved requester and revoke/rotate it when no longer needed.


## Investor and funding request paths

The collaboration hub supports three request kinds: `COLLABORATION`, `INVESTOR_OUTREACH`, and `FUNDING_REQUEST`. Investor outreach records the requester's investment interest. Funding requests additionally record amount, currency, stage, instrument, intended use and an optional pitch-deck URL. These records use the same requester identity, agreement versioning, consent, owner approval, permission and audit infrastructure; submitting a funding or investor request does not itself grant access to private material or create an investment/funding commitment.
