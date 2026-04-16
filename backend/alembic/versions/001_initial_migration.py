"""Initial migration - create projects, generation_jobs, scenes tables

Revision ID: 001
Revises:
Create Date: 2024-04-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('source_type', sa.String(16), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('char_count', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(16), server_default='zh-CN'),
        sa.Column('status', sa.String(16), server_default='draft'),
        sa.Column('latest_job_id', sa.String(32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_projects_created_at', 'projects', ['created_at'])
    op.create_index('idx_projects_latest_job_id', 'projects', ['latest_job_id'])

    # Create generation_jobs table
    op.create_table(
        'generation_jobs',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('project_id', sa.String(32), nullable=False),
        sa.Column('job_type', sa.String(16), nullable=False),
        sa.Column('status', sa.String(16), server_default='queued'),
        sa.Column('stage', sa.String(32), nullable=True),
        sa.Column('progress', sa.Numeric(4, 2), server_default='0.0'),
        sa.Column('attempt', sa.Integer(), server_default='1'),
        sa.Column('error_code', sa.String(64), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result_video_url', sa.Text(), nullable=True),
        sa.Column('result_subtitle_url', sa.Text(), nullable=True),
        sa.Column('result_scene_json_url', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_generation_jobs_project_id', 'generation_jobs', ['project_id'])
    op.create_index('idx_generation_jobs_status', 'generation_jobs', ['status'])
    op.create_index('idx_generation_jobs_stage', 'generation_jobs', ['stage'])

    # Create scenes table
    op.create_table(
        'scenes',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('project_id', sa.String(32), nullable=False),
        sa.Column('current_version', sa.Integer(), server_default='1'),
        sa.Column('scene_order', sa.Integer(), nullable=False),
        sa.Column('template_type', sa.String(32), nullable=False),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('voiceover', sa.Text(), nullable=False),
        sa.Column('screen_text', postgresql.JSON(), nullable=False),
        sa.Column('duration_sec', sa.Integer(), nullable=False),
        sa.Column('pace', sa.String(16), nullable=True),
        sa.Column('transition', sa.String(16), nullable=True),
        sa.Column('visual_params', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_scenes_project_id', 'scenes', ['project_id'])
    op.create_index('idx_scenes_project_id_scene_order', 'scenes', ['project_id', 'scene_order'])


def downgrade() -> None:
    op.drop_table('scenes')
    op.drop_table('generation_jobs')
    op.drop_table('projects')
