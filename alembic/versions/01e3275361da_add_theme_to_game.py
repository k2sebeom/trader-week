"""Add theme to game

Revision ID: 01e3275361da
Revises: eb035599fe8d
Create Date: 2024-08-12 17:44:50.817109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01e3275361da'
down_revision: Union[str, None] = 'eb035599fe8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('theme', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'theme')
    # ### end Alembic commands ###
