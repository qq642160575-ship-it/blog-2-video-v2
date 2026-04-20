"""add scene v3 fields

Revision ID: b1c2d3e4f5a6
Revises: 33f45bc9de89
Create Date: 2026-04-20

新增5个 v3 叙事质量字段到 scenes 表：
- scene_role: hook | body | close
- narrative_stage: opening | build | payoff | close
- emotion_level: 1-5 情绪强度
- hook_type: question | reveal | contrast（仅第1场景）
- quality_score: 0.0-1.0 Hook 质量评分
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = '33f45bc9de89'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('scenes',
        sa.Column('scene_role', sa.String(20), nullable=False, server_default='body')
    )
    op.add_column('scenes',
        sa.Column('narrative_stage', sa.String(20), nullable=False, server_default='build')
    )
    op.add_column('scenes',
        sa.Column('emotion_level', sa.Integer(), nullable=False, server_default='3')
    )
    op.add_column('scenes',
        sa.Column('hook_type', sa.String(20), nullable=True)
    )
    op.add_column('scenes',
        sa.Column('quality_score', sa.Float(), nullable=True)
    )


def downgrade():
    op.drop_column('scenes', 'quality_score')
    op.drop_column('scenes', 'hook_type')
    op.drop_column('scenes', 'emotion_level')
    op.drop_column('scenes', 'narrative_stage')
    op.drop_column('scenes', 'scene_role')
