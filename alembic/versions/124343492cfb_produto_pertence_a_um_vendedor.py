"""produto pertence a um vendedor

Revision ID: 124343492cfb
Revises: 9d292fb07b83
Create Date: 2026-08-03 20:48:04.563635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '124343492cfb'
down_revision: Union[str, Sequence[str], None] = '9d292fb07b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK = 'produtos_vendedor_id_fkey'


def upgrade() -> None:
    """Upgrade schema."""
    # 1. anulável: passa mesmo com a tabela já tendo linhas
    op.add_column('produtos', sa.Column('vendedor_id', sa.Integer(), nullable=True))
    op.create_foreign_key(FK, 'produtos', 'vendedores', ['vendedor_id'], ['id'])

    # 2. backfill: produtos que já existiam ficam com o vendedor mais antigo.
    #    Se não houver nenhum vendedor, o passo 3 falha de propósito — melhor
    #    quebrar aqui do que gravar produto órfão.
    op.execute(
        'UPDATE produtos SET vendedor_id = (SELECT min(id) FROM vendedores) '
        'WHERE vendedor_id IS NULL'
    )

    # 3. sem nulos, a coluna pode ser travada
    op.alter_column('produtos', 'vendedor_id', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(FK, 'produtos', type_='foreignkey')
    op.drop_column('produtos', 'vendedor_id')
