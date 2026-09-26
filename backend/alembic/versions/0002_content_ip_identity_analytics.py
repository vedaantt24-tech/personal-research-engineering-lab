"""Add content classification, requester identity fields and analytics.

The v0.1/v0.2 baseline was metadata-driven, so this migration is intentionally
idempotent for both an older database and a brand-new checkout where the
baseline may already include some of these columns.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_content_ip_identity_analytics"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def has_column(bind, table, column):
    return column in {x["name"] for x in inspect(bind).get_columns(table)}

def has_table(bind, table):
    return table in inspect(bind).get_table_names()

def has_index(bind, table, index):
    return index in {x["name"] for x in inspect(bind).get_indexes(table)}

def upgrade():
    bind = op.get_bind()
    for table, column, default in [
        ("projects", "classification", "PROFESSIONAL"),
        ("research", "classification", "RESEARCH"),
        ("ideas", "classification", "CONCEPT"),
        ("experiments", "classification", "EXPERIMENTAL"),
        ("publications", "classification", "PROFESSIONAL"),
        ("blog_posts", "classification", "PROFESSIONAL"),
    ]:
        if not has_column(bind, table, column):
            op.add_column(table, sa.Column(column, sa.String(length=40), nullable=False, server_default=default))
        idx = f"ix_{table}_{column}"
        if not has_index(bind, table, idx):
            op.create_index(idx, table, [column])
    for name, typ in [
        ("current_learning", sa.Text()), ("research_interests", sa.Text()),
        ("problem_solving", sa.Text()), ("open_to", sa.Text()),
    ]:
        if not has_column(bind, "profiles", name):
            op.add_column("profiles", sa.Column(name, typ, nullable=False, server_default=""))
    if not has_column(bind, "profiles", "avatar_url"):
        op.add_column("profiles", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    for name, typ in [
        ("professional_profile_url", sa.String(length=500)),
        ("website_url", sa.String(length=500)),
        ("signature_name", sa.String(length=200)),
        ("acceptance_ip_hash", sa.String(length=64)),
    ]:
        if not has_column(bind, "collaboration_requests", name):
            op.add_column("collaboration_requests", sa.Column(name, typ, nullable=(name == "professional_profile_url" or name == "website_url" or name == "acceptance_ip_hash"), server_default=None if name != "signature_name" else ""))
    if not has_table(bind, "analytics_events"):
        op.create_table(
            "analytics_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("event_type", sa.String(length=80), nullable=False),
            sa.Column("path", sa.String(length=500), nullable=False),
            sa.Column("entity_type", sa.String(length=120), nullable=True),
            sa.Column("entity_id", sa.String(length=120), nullable=True),
            sa.Column("referrer", sa.String(length=1000), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
    bind = op.get_bind()
    if not has_index(bind, "analytics_events", "ix_analytics_events_event_type"):
        op.create_index("ix_analytics_events_event_type", "analytics_events", ["event_type"])
    if not has_index(bind, "analytics_events", "ix_analytics_events_path"):
        op.create_index("ix_analytics_events_path", "analytics_events", ["path"])
    if not has_index(bind, "analytics_events", "ix_analytics_events_entity_type"):
        op.create_index("ix_analytics_events_entity_type", "analytics_events", ["entity_type"])
    if not has_index(bind, "analytics_events", "ix_analytics_events_created_at"):
        op.create_index("ix_analytics_events_created_at", "analytics_events", ["created_at"])

def downgrade():
    bind = op.get_bind()
    if has_table(bind, "analytics_events"):
        for idx in ["ix_analytics_events_created_at","ix_analytics_events_entity_type","ix_analytics_events_path","ix_analytics_events_event_type"]:
            if has_index(bind, "analytics_events", idx):
                op.drop_index(idx, table_name="analytics_events")
        op.drop_table("analytics_events")
    for col in ["acceptance_ip_hash", "signature_name", "website_url", "professional_profile_url"]:
        if has_column(bind, "collaboration_requests", col): op.drop_column("collaboration_requests", col)
    for col in ["avatar_url", "open_to", "problem_solving", "research_interests", "current_learning"]:
        if has_column(bind, "profiles", col): op.drop_column("profiles", col)
    for table in ["blog_posts", "publications", "experiments", "ideas", "research", "projects"]:
        idx=f"ix_{table}_classification"
        if has_index(bind, table, idx): op.drop_index(idx, table_name=table)
        if has_column(bind, table, "classification"): op.drop_column(table, "classification")
