"""add_assets_table

Revision ID: 42e26d791376
Revises: 49cf3ef49514
Create Date: 2026-04-17 13:29:14.808710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42e26d791376'
down_revision = '49cf3ef49514'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('asset_type', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("(datetime('now'))"), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_project_id'), 'assets', ['project_id'], unique=False)
    op.create_index(op.f('ix_assets_job_id'), 'assets', ['job_id'], unique=False)
    op.create_index(op.f('ix_assets_asset_type'), 'assets', ['asset_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assets_asset_type'), table_name='assets')
    op.drop_index(op.f('ix_assets_job_id'), table_name='assets')
    op.drop_index(op.f('ix_assets_project_id'), table_name='assets')
    op.drop_table('assets')
