"""Add first-class interests, research references and project technologies."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
revision="0003_research_and_technologies"
down_revision="0002_content_ip_identity_analytics"
branch_labels=None
depends_on=None

def has_table(bind, name): return name in inspect(bind).get_table_names()
def has_index(bind, table, name): return name in {x["name"] for x in inspect(bind).get_indexes(table)}

def upgrade():
    bind=op.get_bind()
    if not has_table(bind,"interests"):
        op.create_table("interests", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("name",sa.String(120),nullable=False), sa.Column("published",sa.Boolean(),nullable=False,server_default=sa.true()))
        op.create_index("ix_interests_name","interests",["name"],unique=True)
    if not has_table(bind,"research_references"):
        op.create_table("research_references", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("research_id",sa.Integer(),nullable=False), sa.Column("title",sa.String(400),nullable=False), sa.Column("authors",sa.Text(),nullable=False,server_default=""), sa.Column("venue",sa.String(250),nullable=True), sa.Column("year",sa.Integer(),nullable=True), sa.Column("doi",sa.String(300),nullable=True), sa.Column("url",sa.String(500),nullable=True), sa.Column("citation_text",sa.Text(),nullable=True), sa.ForeignKeyConstraint(["research_id"],["research.id"],ondelete="CASCADE"))
        op.create_index("ix_research_references_research_id","research_references",["research_id"])
    if not has_table(bind,"project_technologies"):
        op.create_table("project_technologies", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("project_id",sa.Integer(),nullable=False), sa.Column("technology",sa.String(120),nullable=False), sa.ForeignKeyConstraint(["project_id"],["projects.id"],ondelete="CASCADE"))
        op.create_index("ix_project_technologies_project_id","project_technologies",["project_id"])
        op.create_index("ix_project_technologies_technology","project_technologies",["technology"])

def downgrade():
    bind=op.get_bind()
    if has_table(bind,"project_technologies"):
        op.drop_table("project_technologies")
    if has_table(bind,"research_references"):
        op.drop_table("research_references")
    if has_table(bind,"interests"):
        if has_index(bind,"interests","ix_interests_name"): op.drop_index("ix_interests_name",table_name="interests")
        op.drop_table("interests")
