# Final Flow Audit

This document is the single source of truth for the platform flow.

## Visitor paths

`/` → `/work` → project case study
`/research` → research detail → references
`/ideas` → idea detail → permission request
`/experiments` → experiment detail → measurements/charts
`/publications` → publication detail
`/notes` → technical note
`/about` → education/skills/experience/achievements/GitHub
`/timeline` → development milestones
`/resume` → current public resume
`/open-to` → current collaboration interests
`/contact` → terms/privacy gated contact
`/collaborate` → collaboration, investor or funding request

## Social reach-out

Header/footer social controls use owner-published `SocialLink` records. Clicking an individual icon opens a modal/popout for that platform; the visitor can open the configured profile or copy the link. The Connect control exposes all published platforms.

## Collaboration / investor / funding

All request types enter `CollaborationRequest`. The request stores the requester identity, purpose, requested rights, agreement version/hash/snapshot, site terms version/hash/snapshot, privacy acknowledgement and typed signature. Investor and funding requests additionally store the relevant investment/funding fields.

Approval creates a `PermissionGrant`. A restricted idea link is a bearer credential whose database record stores only a hash. The shared endpoint checks approval, expiry, revocation and the approved rights before returning fields. Usage is written to `AuditLog`.

## Publishing safety

Any public publish operation requires an explicit API-level `publication_safety_confirmed=true`. Restoring a historical public revision does not bypass the safety gate.

## Data visibility

`PUBLIC` and eligible `UNLISTED` records can reach public APIs. `PRIVATE` and `CONFIDENTIAL` records are excluded from public content endpoints. Permission-required Ideas return a high-level subset only.
