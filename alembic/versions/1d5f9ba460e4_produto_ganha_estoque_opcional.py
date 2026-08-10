"""produto ganha estoque opcional

Revision ID: 1d5f9ba460e4
Revises: 124343492cfb
Create Date: 2026-08-10 16:04:09.942003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d5f9ba460e4'
down_revision: Union[str, Sequence[str], None] = '124343492cfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CHECK_ESTOQUE = "produtos_estoque_nao_negativo"


def upgrade() -> None:
    """Upgrade schema."""
    # nullable: os produtos que já existem ficam com NULL = estoque não controlado
    op.add_column("produtos", sa.Column("estoque", sa.Integer(), nullable=True))
    # o autogenerate não detecta CHECK (mesma limitação do UNIQUE, lição 28)
    op.create_check_constraint(CHECK_ESTOQUE, "produtos", "estoque >= 0")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(CHECK_ESTOQUE, "produtos", type_="check")
    op.drop_column("produtos", "estoque")
