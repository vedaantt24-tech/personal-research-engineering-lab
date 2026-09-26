"""Add GitHub/profile integration fields and experiment data points."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
revision="0005_integrations_resume_experiment_data"
down_revision="0004_permissions_media"
branch_labels=None
depends_on=None

def colnames(bind, table):
    return {c["name"] for c in inspect(bind).get_columns(table)}

def upgrade():
    bind=op.get_bind()
    cols=colnames(bind,"profiles")
    for name, typ, default in [
        ("github_username", sa.String(120), None),
        ("github_featured_repos", sa.Text(), "[]"),
        ("orcid_url", sa.String(500), None),
        ("google_scholar_url", sa.String(500), None),
        ("arxiv_url", sa.String(500), None),
    ]:
        if name not in cols:
            kwargs={"nullable":default is None}
            if default is not None: kwargs["server_default"]=default
            op.add_column("profiles",sa.Column(name,typ,**kwargs))
            if default is not None: op.alter_column("profiles",name,server_default=None)
    if "experiment_data" not in inspect(bind).get_table_names():
        op.create_table(
            "experiment_data",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("experiment_id",sa.Integer(),nullable=False),
            sa.Column("series",sa.String(100),nullable=False,server_default="default"),
            sa.Column("x_label",sa.String(160),nullable=True),
            sa.Column("x_value",sa.Float(),nullable=True),
            sa.Column("y_value",sa.Float(),nullable=False),
            sa.Column("unit",sa.String(80),nullable=True),
            sa.Column("note",sa.String(500),nullable=True),
            sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
            sa.ForeignKeyConstraint(["experiment_id"],["experiments.id"],ondelete="CASCADE"),
        )
        op.create_index("ix_experiment_data_experiment_id","experiment_data",["experiment_id"])
        op.create_index("ix_experiment_data_series","experiment_data",["series"])

def downgrade():
    bind=op.get_bind()
    if "experiment_data" in inspect(bind).get_table_names():
        op.drop_index("ix_experiment_data_series",table_name="experiment_data")
        op.drop_index("ix_experiment_data_experiment_id",table_name="experiment_data")
        op.drop_table("experiment_data")
    cols=colnames(bind,"profiles")
    for name in ["arxiv_url","google_scholar_url","orcid_url","github_featured_repos","github_username"]:
        if name in cols: op.drop_column("profiles",name)
