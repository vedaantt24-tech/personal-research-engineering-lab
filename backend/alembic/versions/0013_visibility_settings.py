"""add visibility settings store

Revision ID: 0013_visibility_settings
Revises: 0012_investor_and_funding_requests
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision="0013_visibility_settings"
down_revision="0012_investor_and_funding_requests"
branch_labels=None
depends_on=None

def upgrade():
    bind=op.get_bind(); insp=inspect(bind)
    tables=set(insp.get_table_names())
    if "visibility_settings" not in tables:
        op.create_table(
            "visibility_settings",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("key", sa.String(120), nullable=False),
            sa.Column("default_visibility", sa.String(20), nullable=False, server_default="PRIVATE"),
            sa.Column("notes", sa.Text(), nullable=False, server_default=""),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_visibility_settings_key", "visibility_settings", ["key"], unique=True)

def downgrade():
    bind=op.get_bind(); insp=inspect(bind)
    if "visibility_settings" in insp.get_table_names():
        op.drop_index("ix_visibility_settings_key", table_name="visibility_settings")
        op.drop_table("visibility_settings")
