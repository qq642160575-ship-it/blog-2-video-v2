"""add_job_logs_table

Revision ID: 49cf3ef49514
Revises: ad6ddad88123
Create Date: 2026-04-17 13:13:38.540236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49cf3ef49514'
down_revision = 'ad6ddad88123'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'job_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('stage', sa.String(), nullable=False),
        sa.Column('level', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("(datetime('now'))"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_logs_job_id'), 'job_logs', ['job_id'], unique=False)
    op.create_index(op.f('ix_job_logs_project_id'), 'job_logs', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_job_logs_project_id'), table_name='job_logs')
    op.drop_index(op.f('ix_job_logs_job_id'), table_name='job_logs')
    op.drop_table('job_logs')
