"""nome unico em produtos vendedores clientes

Revision ID: 2c0c6fcf55db
Revises: 1f3693142ae9
Create Date: 2026-07-21 20:09:06.761217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c0c6fcf55db'
down_revision: Union[str, Sequence[str], None] = '1f3693142ae9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Escrito à mão: o autogenerate NÃO detecta constraints UNIQUE.
    # Troca o índice comum (index=True antigo) por uma constraint única.
    op.drop_index('ix_produtos_nome', table_name='produtos')
    op.create_unique_constraint('uq_produtos_nome', 'produtos', ['nome'])

    op.drop_index('ix_vendedores_nome', table_name='vendedores')
    op.create_unique_constraint('uq_vendedores_nome', 'vendedores', ['nome'])

    op.drop_index('ix_clientes_nome', table_name='clientes')
    op.create_unique_constraint('uq_clientes_nome', 'clientes', ['nome'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_clientes_nome', 'clientes', type_='unique')
    op.create_index('ix_clientes_nome', 'clientes', ['nome'])

    op.drop_constraint('uq_vendedores_nome', 'vendedores', type_='unique')
    op.create_index('ix_vendedores_nome', 'vendedores', ['nome'])

    op.drop_constraint('uq_produtos_nome', 'produtos', type_='unique')
    op.create_index('ix_produtos_nome', 'produtos', ['nome'])
