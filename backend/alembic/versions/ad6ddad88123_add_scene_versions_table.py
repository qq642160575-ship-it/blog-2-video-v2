"""add_scene_versions_table

Revision ID: ad6ddad88123
Revises: 001
Create Date: 2026-04-17 10:45:33.363698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad6ddad88123'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'scene_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scene_id', sa.String(length=32), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(length=32), nullable=False),
        sa.Column('template_type', sa.String(length=32), nullable=False),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('voiceover', sa.Text(), nullable=False),
        sa.Column('screen_text', sa.JSON(), nullable=False),
        sa.Column('duration_sec', sa.Integer(), nullable=False),
        sa.Column('pace', sa.String(length=16), nullable=True),
        sa.Column('transition', sa.String(length=16), nullable=True),
        sa.Column('visual_params', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scene_versions_scene_id'), 'scene_versions', ['scene_id'], unique=False)
    op.create_index(op.f('ix_scene_versions_project_id'), 'scene_versions', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scene_versions_project_id'), table_name='scene_versions')
    op.drop_index(op.f('ix_scene_versions_scene_id'), table_name='scene_versions')
    op.drop_table('scene_versions')
