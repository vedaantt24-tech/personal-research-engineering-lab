"""Give auxiliary content records the same Draft/Review/Published/Archived workflow."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
revision="0008_unified_content_workflow"
down_revision="0007_terms_consent_snapshots"
branch_labels=None
depends_on=None

TABLES=["skills","education","experiences","social_links","resumes","interests"]

def has_column(bind, table, column):
    return column in {c["name"] for c in inspect(bind).get_columns(table)}

def has_index(bind, table, index):
    return index in {x["name"] for x in inspect(bind).get_indexes(table)}

def upgrade():
    bind=op.get_bind()
    for table in TABLES:
        if not has_column(bind, table, "state"):
            op.add_column(table, sa.Column("state", sa.String(40), nullable=False, server_default="PUBLISHED"))
            op.alter_column(table,"state",server_default=None)
        idx=f"ix_{table}_state"
        if not has_index(bind, table, idx):
            op.create_index(idx, table, ["state"])

def downgrade():
    bind=op.get_bind()
    for table in reversed(TABLES):
        idx=f"ix_{table}_state"
        if has_index(bind, table, idx):
            op.drop_index(idx, table_name=table)
        if has_column(bind, table, "state"):
            op.drop_column(table,"state")
