"""add_ai_logs_table

Revision ID: 33f45bc9de89
Revises: 42e26d791376
Create Date: 2026-04-17 15:32:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33f45bc9de89'
down_revision = '42e26d791376'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_logs table
    op.create_table(
        'ai_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('operation', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=True),
        sa.Column('tokens_output', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_ai_logs_job_id', 'ai_logs', ['job_id'])
    op.create_index('ix_ai_logs_project_id', 'ai_logs', ['project_id'])
    op.create_index('ix_ai_logs_operation', 'ai_logs', ['operation'])


def downgrade() -> None:
    op.drop_index('ix_ai_logs_operation', table_name='ai_logs')
    op.drop_index('ix_ai_logs_project_id', table_name='ai_logs')
    op.drop_index('ix_ai_logs_job_id', table_name='ai_logs')
    op.drop_table('ai_logs')
