"""final permission scope and contact terms snapshot

Revision ID: 0009_final_permission_scope
Revises: 0008_unified_content_workflow
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0009_final_permission_scope"
down_revision = "0008_unified_content_workflow"
branch_labels = None
depends_on = None

def has_column(bind, table, column):
    return column in {c["name"] for c in inspect(bind).get_columns(table)}

def upgrade():
    bind = op.get_bind()
    if not has_column(bind, "contact_messages", "site_terms_body_snapshot"):
        op.add_column(
            "contact_messages",
            sa.Column("site_terms_body_snapshot", sa.Text(), nullable=False, server_default=""),
        )
        op.alter_column("contact_messages", "site_terms_body_snapshot", server_default=None)

def downgrade():
    bind = op.get_bind()
    if has_column(bind, "contact_messages", "site_terms_body_snapshot"):
        op.drop_column("contact_messages", "site_terms_body_snapshot")
