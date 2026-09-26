"""Initial baseline schema using SQLAlchemy metadata.

Autogenerate a conventional migration after changing models in future releases.
"""
from alembic import op
from app.db.session import Base
import app.models.entities  # noqa: F401

revision="0001_initial"
down_revision=None
branch_labels=None
depends_on=None

def upgrade(): Base.metadata.create_all(bind=op.get_bind())
def downgrade(): Base.metadata.drop_all(bind=op.get_bind())
