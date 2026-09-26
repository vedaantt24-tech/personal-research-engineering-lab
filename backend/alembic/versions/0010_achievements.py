"""add achievements content entity

Revision ID: 0010_achievements
Revises: 0009_final_permission_scope
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision="0010_achievements"
down_revision="0009_final_permission_scope"
branch_labels=None
depends_on=None

def upgrade():
    bind=op.get_bind()
    if "achievements" not in inspect(bind).get_table_names():
        op.create_table(
            "achievements",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("title",sa.String(250),nullable=False),
            sa.Column("organization",sa.String(250),nullable=True),
            sa.Column("date_label",sa.String(100),nullable=True),
            sa.Column("description",sa.Text(),nullable=False,server_default=""),
            sa.Column("link",sa.String(500),nullable=True),
            sa.Column("published",sa.Boolean(),nullable=False,server_default=sa.false()),
            sa.Column("state",sa.String(20),nullable=False,server_default="DRAFT"),
        )
        op.create_index("ix_achievements_state","achievements",["state"],unique=False)
        op.alter_column("achievements","description",server_default=None)
        op.alter_column("achievements","published",server_default=None)
        op.alter_column("achievements","state",server_default=None)

def downgrade():
    bind=op.get_bind()
    if "achievements" in inspect(bind).get_table_names():
        op.drop_table("achievements")
