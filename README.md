# Personal Research, Innovation & Engineering Lab — Final Consolidated Release

A single-owner personal platform combining an engineering portfolio, research notebook, ideas lab, experiment log, publication library, editable profile/CV, real analytics and a controlled collaboration/permission workflow.

## Current checkpoint

**Requested application scope: 100% implemented in this consolidated source tree.** See `docs/FEATURE-CHECKLIST.md` and `docs/FINAL-VERIFICATION.md` for the complete flow audit and verification boundary.

### Public platform
- Home with live featured work
- About with live profile, interests, skills, education and experience
- Work / project case studies
- Research records with structured references
- Ideas Lab with high-level disclosure for permission-required ideas
- Experiments notebook
- Publications / preprints / reports
- Technical Notes
- Resume page
- Open To page backed by the owner profile
- Contact form
- Collaboration/use-request form, including general collaboration, Investor / Investment Discussion, and Funding Request paths
- Terms, privacy and intellectual-property pages
- Responsive engineering/editorial design
- Real page-view analytics events
- Public search limited to explicitly published public content
- Server-rendered public detail pages for stronger crawlability
- Restricted-access link usage is recorded in the audit trail
- Dynamic detail metadata, canonical URLs, JSON-LD and dynamic sitemap entries

### Owner CMS
- Single-owner secure login
- HTTP-only session cookie plus CSRF protection for mutating owner actions
- Profile editor including learning, research interests, problem-solving approach and Open To
- CRUD for projects, research, ideas, experiments, publications, notes, skills, interests, education, experience, social links and resume records
- Draft / Review / Published / Archived workflow
- Public / Unlisted / Private / Confidential visibility
- Public classification field
- API-enforced publishing safety confirmation
- Structured project technologies and research references
- Media library + content attachments
- Collaboration request inbox
- Approve / reject / request-info flow
- Permission grant records and revocation
- Versioned agreement manager with SHA-256 integrity hashes and request-time agreement body snapshots
- Site-terms version/hash and privacy acknowledgement evidence on collaboration/contact flows
- Time-limited restricted-access bearer links for approved idea details
- Contact-message inbox and read state
- Audit log
- Append-only content revision history with restore-as-new-version
- CI workflow for backend/frontend validation
- Automatic PDF resume generation
- Owner-controlled visibility policy defaults
- Searchable public content index
- Local or S3-compatible media storage adapter
- Optional Turnstile verification
- Optional SMTP notifications
- 30-day analytics report
- Numeric experiment measurements and public charts
- ORCID / Google Scholar / arXiv profile links
- GitHub repository integration with owner-controlled discovery and selection
- Unified social Connect popout with owner-configured multi-platform icon links
- Optional Crossref DOI metadata lookup for publications
- Investor / Funding Request collaboration records with funding amount, currency, stage, instrument, use-of-funds and optional pitch deck fields

## End-to-end permission flow

```text
Public high-level idea
        ↓
Collaborate / Use Request
        ↓
Identity + intended use + requested rights
        ↓
Current agreement version + SHA-256
        ↓
Typed signature + explicit acceptance
        ↓
Owner review
   ┌────┼─────────────┐
Approve  Reject   Need info
   ↓        ↓          ↓
Grant    Revoke     Await reply
   ↓
Optional restricted-access link
   ↓
Expire / Revoke
   ↓
Audit trail
```

## Data safety rules

- `PUBLIC` is explicit.
- `UNLISTED` is direct-link only.
- `PRIVATE` and `CONFIDENTIAL` are never returned from public content endpoints.
- Permission-required public ideas expose only a high-level subset through the public API.
- Public publication is blocked unless the owner completes the safety confirmation.
- Agreement versions cannot be rewritten after creation; create a new version instead.
- Analytics are recorded, not fabricated.
- Restricted-access tokens are stored only as hashes.

## Local run

1. Copy `.env.example` to `.env`.
2. Replace `OWNER_EMAIL`, `OWNER_PASSWORD` and `SECRET_KEY`.
3. Start services with `docker compose up --build`.
4. Public site: `http://localhost:3000`
5. API docs: `http://localhost:8000/docs`
6. For Docker server-side rendering, keep `INTERNAL_API_URL=http://backend:8000/api/v1`.
6. Owner CMS: `http://localhost:3000/admin/login`

For a fresh production database, prefer:

```bash
alembic -c alembic.ini upgrade head
```

and set `AUTO_CREATE_TABLES=false`.

## Final verification status

See `docs/FINAL-FLOW-AUDIT.md`, `docs/FEATURE-CHECKLIST.md` and `docs/FINAL-VERIFICATION.md` for the consolidated implementation matrix.

- Python compile check: passed.
- Backend integration tests: **17 passed**.
- Alembic upgrade/downgrade from an empty SQLite database through **0012**: passed.
- Frontend TypeScript/TSX source checks: passed at source level.
- ZIP integrity: checked before delivery.
- Docker image build and browser automation remain dependent on environment/runtime availability.
- Full `npm install` / `next build`: not claimable in this environment because the public npm registry cannot be resolved. CI is configured to run typecheck, lint and build in a connected environment.

## Legal note

The agreement and legal-page text are implementation templates, not legal advice. Before relying on the workflow for commercially important ideas, patents, confidential disclosures or licenses, have the final wording and disclosure process reviewed by qualified counsel in the relevant jurisdiction.

## Frontend preview

Source-based visual previews are included at `docs/frontend-preview-desktop.png` and `docs/frontend-preview-mobile.png`. They represent the intended homepage composition using the same visual direction as the implemented Next.js pages; they are not a substitute for browser QA. A static HTML preview is also included at `docs/frontend-preview.html`.
