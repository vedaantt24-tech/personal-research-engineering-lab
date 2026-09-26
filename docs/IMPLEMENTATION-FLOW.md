# Platform flow — keep this intact

## Public discovery

Home → Work / Research / Ideas Lab / Experiments / Publications → detail page → Contact or Collaborate.

Only content explicitly published by the owner is returned by public collection endpoints. `UNLISTED` content is not listed but can be opened through its direct slug. `PRIVATE` and `CONFIDENTIAL` content is not returned publicly.

## Idea disclosure

A permission-required idea is shown publicly at a high level. Enabling implementation details are deliberately omitted from the public idea API. The owner can keep detailed implementation, source code, datasets and other sensitive material private.

## Collaboration / idea-use request

1. Visitor selects an idea (optional) and opens `/collaborate?idea=IDEA-...`.
2. Site loads the currently active agreement version and its SHA-256 hash.
3. Visitor supplies name, email, professional profile/website, intended purpose and requested rights.
4. Visitor types a signature matching the submitted full name and explicitly accepts that exact agreement version.
5. API re-checks the agreement version/hash; a stale version is rejected.
6. Request is stored with requester identity, requested rights, agreement version/hash, acceptance timestamp and a privacy-conscious network-address hash.
7. Owner sees the request in the private CMS.
8. Owner can approve, reject/revoke, or request more information.
9. Approval creates a separate `PermissionGrant` record. Rejection revokes an existing grant.
10. The request and administrative actions are recorded in `AuditLog`.

## Owner publishing flow

Create / edit → Draft → Review → safety check → Publish.

The API itself blocks `state=PUBLISHED` + `visibility=PUBLIC` unless `publication_safety_confirmed=true` is supplied. The CMS shows a checklist before allowing that action.

The safety check is intended to reduce accidental publication of passwords, API keys, private documents, confidential employer information, proprietary details and sensitive research disclosures.

## Agreement lifecycle

Agreement versions are immutable after creation. To change terms, create a new version (for example 1.1). Activating the new version deactivates the prior version for that agreement type. Requests preserve the exact accepted version/hash even after a newer version exists.

## Analytics

Public page views and selected interaction events are stored as real records. The admin dashboard reports recorded data only; it does not fabricate visitor numbers.


## v0.5 integration layer

The existing owner-controlled flow is preserved. v0.5 adds optional GitHub repository sync, measurable experiment data, analytics reporting, automatic resume PDF generation, optional email notifications, optional Turnstile verification, and pluggable media storage. These additions never bypass the public/private/confidential or permission/audit boundaries.


## Social reach-out flow

Owner publishes SocialLink records → public site renders icon buttons → clicking an individual icon opens a reach-out popout → visitor can open the configured profile in a new tab or return to the full multi-platform list. Social links are independent of restricted-content permissions and do not grant idea-use rights.
