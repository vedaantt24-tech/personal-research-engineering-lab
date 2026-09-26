"""Persist site-terms/consent evidence for contact and collaboration flows."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision="0007_terms_consent_snapshots"
down_revision="0006_content_revisions_and_agreement_snapshot"
branch_labels=None
depends_on=None

def has_column(bind, table, column):
    return column in {c["name"] for c in inspect(bind).get_columns(table)}

def upgrade():
    bind=op.get_bind()
    collaboration=[
        ("site_terms_version", sa.String(40), True, None),
        ("site_terms_sha256", sa.String(64), True, None),
        ("site_terms_body_snapshot", sa.Text(), False, ""),
        ("privacy_acknowledged_at", sa.DateTime(timezone=True), True, None),
    ]
    for name, typ, nullable, default in collaboration:
        if not has_column(bind,"collaboration_requests",name):
            kwargs={"nullable":nullable}
            if default is not None: kwargs["server_default"]=default
            op.add_column("collaboration_requests",sa.Column(name,typ,**kwargs))
            if default is not None: op.alter_column("collaboration_requests",name,server_default=None)
    contact=[
        ("site_terms_version", sa.String(40), True, None),
        ("site_terms_sha256", sa.String(64), True, None),
        ("terms_accepted_at", sa.DateTime(timezone=True), True, None),
    ]
    for name, typ, nullable, default in contact:
        if not has_column(bind,"contact_messages",name):
            op.add_column("contact_messages",sa.Column(name,typ,nullable=nullable))

def downgrade():
    bind=op.get_bind()
    for name in ["terms_accepted_at","site_terms_sha256","site_terms_version"]:
        if has_column(bind,"contact_messages",name): op.drop_column("contact_messages",name)
    for name in ["privacy_acknowledged_at","site_terms_body_snapshot","site_terms_sha256","site_terms_version"]:
        if has_column(bind,"collaboration_requests",name): op.drop_column("collaboration_requests",name)
