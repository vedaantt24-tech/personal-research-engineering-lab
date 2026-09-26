"""Add controlled access tokens, contact audit hash and media relationships."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0004_permissions_media"
down_revision = "0003_research_and_technologies"
branch_labels = None
depends_on = None

def has_table(bind, name):
    return name in inspect(bind).get_table_names()

def has_column(bind, table, column):
    return column in {c["name"] for c in inspect(bind).get_columns(table)}

def has_index(bind, table, index):
    return index in {x["name"] for x in inspect(bind).get_indexes(table)}

def upgrade():
    bind = op.get_bind()
    if not has_column(bind, "permission_grants", "access_token_hash"):
        op.add_column("permission_grants", sa.Column("access_token_hash", sa.String(64), nullable=True))
    if not has_index(bind, "permission_grants", "ix_permission_grants_access_token_hash"):
        op.create_index("ix_permission_grants_access_token_hash", "permission_grants", ["access_token_hash"], unique=True)
    if not has_column(bind, "permission_grants", "access_token_issued_at"):
        op.add_column("permission_grants", sa.Column("access_token_issued_at", sa.DateTime(timezone=True), nullable=True))
    if not has_column(bind, "contact_messages", "network_ip_hash"):
        op.add_column("contact_messages", sa.Column("network_ip_hash", sa.String(64), nullable=True))
    if not has_index(bind, "contact_messages", "ix_contact_messages_network_ip_hash"):
        op.create_index("ix_contact_messages_network_ip_hash", "contact_messages", ["network_ip_hash"])
    if not has_table(bind, "media_links"):
        op.create_table(
            "media_links",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("media_id", sa.Integer(), nullable=False),
            sa.Column("entity_type", sa.String(80), nullable=False),
            sa.Column("entity_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(80), nullable=False, server_default="attachment"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["media_id"], ["media.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_media_links_media_id", "media_links", ["media_id"])
        op.create_index("ix_media_links_entity_type", "media_links", ["entity_type"])
        op.create_index("ix_media_links_entity_id", "media_links", ["entity_id"])

def downgrade():
    bind = op.get_bind()
    if has_table(bind, "media_links"):
        op.drop_index("ix_media_links_entity_id", table_name="media_links")
        op.drop_index("ix_media_links_entity_type", table_name="media_links")
        op.drop_index("ix_media_links_media_id", table_name="media_links")
        op.drop_table("media_links")
    if has_index(bind, "contact_messages", "ix_contact_messages_network_ip_hash"):
        op.drop_index("ix_contact_messages_network_ip_hash", table_name="contact_messages")
    if has_column(bind, "contact_messages", "network_ip_hash"):
        op.drop_column("contact_messages", "network_ip_hash")
    if has_index(bind, "permission_grants", "ix_permission_grants_access_token_hash"):
        op.drop_index("ix_permission_grants_access_token_hash", table_name="permission_grants")
    if has_column(bind, "permission_grants", "access_token_hash"):
        op.drop_column("permission_grants", "access_token_hash")
    if has_column(bind, "permission_grants", "access_token_issued_at"):
        op.drop_column("permission_grants", "access_token_issued_at")
