"""add investor and funding request collaboration types

Revision ID: 0012_investor_and_funding_requests
Revises: 0011_profile_visibility_and_timeline
"""
import hashlib
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

revision="0012_investor_and_funding_requests"
down_revision="0011_profile_visibility_and_timeline"
branch_labels=None
depends_on=None

def upgrade():
    bind=op.get_bind(); insp=inspect(bind)
    cols={c["name"] for c in insp.get_columns("collaboration_requests")}
    additions=[
        ("request_kind", sa.Column("request_kind", sa.String(40), nullable=False, server_default="COLLABORATION")),
        ("investment_interest", sa.Column("investment_interest", sa.String(500), nullable=True)),
        ("funding_amount", sa.Column("funding_amount", sa.Float(), nullable=True)),
        ("funding_currency", sa.Column("funding_currency", sa.String(3), nullable=False, server_default="INR")),
        ("funding_stage", sa.Column("funding_stage", sa.String(120), nullable=True)),
        ("funding_instrument", sa.Column("funding_instrument", sa.String(120), nullable=True)),
        ("funding_use", sa.Column("funding_use", sa.Text(), nullable=True)),
        ("pitch_deck_url", sa.Column("pitch_deck_url", sa.String(500), nullable=True)),
    ]
    for name,col in additions:
        if name not in cols:
            op.add_column("collaboration_requests",col)
            if name in {"request_kind"}: op.alter_column("collaboration_requests",name,server_default=None)
            if name in {"funding_currency"}: op.alter_column("collaboration_requests",name,server_default=None)
    idx_names={i["name"] for i in insp.get_indexes("collaboration_requests")}
    if "ix_collaboration_requests_request_kind" not in idx_names:
        op.create_index("ix_collaboration_requests_request_kind","collaboration_requests",["request_kind"],unique=False)
    agreements=[
        ("INVESTOR_DISCUSSION","1.0","Investor Discussion Agreement",
         "INVESTOR DISCUSSION AGREEMENT — TEMPLATE\n\nThis template records a request to discuss investment, strategic investment or related support. It does not create an investment commitment, securities offering, partnership, agency relationship or transfer of ownership. Any investment terms must be documented in separate definitive agreements reviewed for the relevant jurisdiction."),
        ("FUNDING_REQUEST","1.0","Funding Request Agreement",
         "FUNDING REQUEST AGREEMENT — TEMPLATE\n\nThis template records a request for funding or financial support for a project, research activity, product or concept. Submission does not create a funding commitment. Amounts, valuation, securities, use of funds and other financial terms require separate written documentation where applicable."),
    ]
    for kind,version,title,body in agreements:
        exists=bind.execute(text("SELECT 1 FROM agreement_templates WHERE agreement_type=:kind LIMIT 1"),{"kind":kind}).scalar()
        if not exists:
            bind.execute(text("INSERT INTO agreement_templates (agreement_type,version,title,body,sha256,active,created_at) VALUES (:kind,:version,:title,:body,:sha256,:active,CURRENT_TIMESTAMP)"),{"kind":kind,"version":version,"title":title,"body":body,"sha256":hashlib.sha256(body.encode()).hexdigest(),"active":True})

def downgrade():
    bind=op.get_bind(); insp=inspect(bind)
    idx_names={i["name"] for i in insp.get_indexes("collaboration_requests")}
    if "ix_collaboration_requests_request_kind" in idx_names: op.drop_index("ix_collaboration_requests_request_kind",table_name="collaboration_requests")
    cols={c["name"] for c in insp.get_columns("collaboration_requests")}
    for name in ["pitch_deck_url","funding_use","funding_instrument","funding_stage","funding_currency","funding_amount","investment_interest","request_kind"]:
        if name in cols: op.drop_column("collaboration_requests",name)
    bind.execute(text("DELETE FROM agreement_templates WHERE agreement_type IN ('INVESTOR_DISCUSSION','FUNDING_REQUEST')"))
