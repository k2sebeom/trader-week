"""Add thumbnail to company

Revision ID: 56890c529c6d
Revises: 01e3275361da
Create Date: 2024-08-12 18:29:44.431577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56890c529c6d'
down_revision: Union[str, None] = '01e3275361da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('companies', sa.Column('thumbnail', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('companies', 'thumbnail')
    # ### end Alembic commands ###
