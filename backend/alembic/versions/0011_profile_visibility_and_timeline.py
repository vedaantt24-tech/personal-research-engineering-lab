"""add profile contact visibility and timeline entries

Revision ID: 0011_profile_visibility_and_timeline
Revises: 0010_achievements
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision="0011_profile_visibility_and_timeline"
down_revision="0010_achievements"
branch_labels=None
depends_on=None

def upgrade():
    bind=op.get_bind(); insp=inspect(bind)
    cols={c["name"] for c in insp.get_columns("profiles")}
    if "contact_email_public" not in cols:
        op.add_column("profiles", sa.Column("contact_email_public", sa.Boolean(), nullable=False, server_default=sa.false()))
        op.alter_column("profiles", "contact_email_public", server_default=None)
    if "timeline_entries" not in insp.get_table_names():
        op.create_table(
            "timeline_entries",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("date_label", sa.String(100), nullable=False, server_default=""),
            sa.Column("title", sa.String(250), nullable=False),
            sa.Column("category", sa.String(100), nullable=False, server_default="Milestone"),
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
            sa.Column("link", sa.String(500), nullable=True),
            sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("state", sa.String(20), nullable=False, server_default="PUBLISHED"),
        )
        op.create_index("ix_timeline_entries_category", "timeline_entries", ["category"], unique=False)
        op.create_index("ix_timeline_entries_state", "timeline_entries", ["state"], unique=False)
        op.alter_column("timeline_entries", "date_label", server_default=None)
        op.alter_column("timeline_entries", "category", server_default=None)
        op.alter_column("timeline_entries", "description", server_default=None)
        op.alter_column("timeline_entries", "published", server_default=None)
        op.alter_column("timeline_entries", "state", server_default=None)

def downgrade():
    bind=op.get_bind(); insp=inspect(bind)
    if "timeline_entries" in insp.get_table_names():
        op.drop_table("timeline_entries")
    cols={c["name"] for c in insp.get_columns("profiles")}
    if "contact_email_public" in cols:
        op.drop_column("profiles", "contact_email_public")
