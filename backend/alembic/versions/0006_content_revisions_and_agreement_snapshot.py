"""Add immutable content revisions and agreement snapshots."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0006_content_revisions_and_agreement_snapshot"
down_revision = "0005_integrations_resume_experiment_data"
branch_labels = None
depends_on = None

def has_table(bind, name):
    return name in inspect(bind).get_table_names()

def has_column(bind, table, column):
    return column in {c["name"] for c in inspect(bind).get_columns(table)}

def has_index(bind, table, index):
    return index in {x["name"] for x in inspect(bind).get_indexes(table)}

def upgrade():
    bind=op.get_bind()
    if not has_column(bind,"collaboration_requests","agreement_body_snapshot"):
        op.add_column("collaboration_requests", sa.Column("agreement_body_snapshot", sa.Text(), nullable=False, server_default=""))
        op.alter_column("collaboration_requests","agreement_body_snapshot",server_default=None)
    if not has_table(bind,"content_revisions"):
        op.create_table(
            "content_revisions",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("entity_type",sa.String(80),nullable=False),
            sa.Column("entity_id",sa.Integer(),nullable=False),
            sa.Column("version_no",sa.Integer(),nullable=False),
            sa.Column("snapshot_json",sa.Text(),nullable=False),
            sa.Column("actor_email",sa.String(320),nullable=False),
            sa.Column("change_note",sa.Text(),nullable=True),
            sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        )
        op.create_index("ix_content_revisions_entity_type","content_revisions",["entity_type"])
        op.create_index("ix_content_revisions_entity_id","content_revisions",["entity_id"])
        op.create_index("ix_content_revisions_actor_email","content_revisions",["actor_email"])
        op.create_index("ix_content_revisions_entity_version","content_revisions",["entity_type","entity_id","version_no"],unique=True)

def downgrade():
    bind=op.get_bind()
    if has_index(bind,"content_revisions","ix_content_revisions_entity_version"):
        op.drop_index("ix_content_revisions_entity_version",table_name="content_revisions")
    for idx in ["ix_content_revisions_actor_email","ix_content_revisions_entity_id","ix_content_revisions_entity_type"]:
        if has_index(bind,"content_revisions",idx): op.drop_index(idx,table_name="content_revisions")
    if has_table(bind,"content_revisions"): op.drop_table("content_revisions")
    if has_column(bind,"collaboration_requests","agreement_body_snapshot"):
        op.drop_column("collaboration_requests","agreement_body_snapshot")
