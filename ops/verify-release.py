from pathlib import Path
import ast, re, zipfile, sys

ROOT=Path(__file__).resolve().parents[1]
required_files=[
    'frontend/src/app/page.tsx','frontend/src/app/collaborate/page.tsx','frontend/src/components/SocialHub.tsx',
    'frontend/src/components/ContentStudio.tsx','backend/app/api/routes.py','backend/app/models/entities.py',
    'backend/alembic/versions/0012_investor_and_funding_requests.py','docs/FEATURE-CHECKLIST.md','docs/FINAL-FLOW-AUDIT.md','frontend/src/components/VisibilitySettings.tsx'
]
missing=[p for p in required_files if not (ROOT/p).exists()]
if missing:
    raise SystemExit(f'Missing required files: {missing}')

for path in ROOT.glob('backend/**/*.py'):
    ast.parse(path.read_text(encoding='utf-8'))

routes=(ROOT/'backend/app/api/routes.py').read_text(encoding='utf-8')
for route in ['/collaboration-requests','/public/social-links','/public/ideas/{slug}','/shared/{token}/ideas/{slug}','/admin/requests/{request_id}/access-link','/admin/audit-logs','/admin/visibility-settings']:
    if route not in routes:
        raise SystemExit(f'Missing route contract: {route}')

social=(ROOT/'frontend/src/components/SocialHub.tsx').read_text(encoding='utf-8')
for needle in ['instagram','linkedin','github','selected','open profile','see all platforms']:
    if needle not in social.lower():
        raise SystemExit(f'Missing social UI contract: {needle}')

collab=(ROOT/'frontend/src/app/collaborate/page.tsx').read_text(encoding='utf-8')
for needle in ['INVESTOR_OUTREACH','FUNDING_REQUEST','Agreement','signature_name','privacy_acknowledged']:
    if needle not in collab:
        raise SystemExit(f'Missing collaboration contract: {needle}')

for bad in ['.env', '.db', '.pyc']:
    pass

print('FINAL_SOURCE_AUDIT_OK')
