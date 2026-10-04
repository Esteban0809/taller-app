"""seguimiento del cliente: token público y aprobación de presupuesto

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-04 20:00:00

"""
import secrets
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('reparaciones') as batch:
        batch.add_column(sa.Column('token_seguimiento', sa.String(length=32), nullable=True))
        batch.add_column(sa.Column('presupuesto_aprobado_at', sa.DateTime(), nullable=True))

    # Las reparaciones que ya existían también necesitan su enlace
    conexion = op.get_bind()
    reparaciones = sa.table('reparaciones', sa.column('id', sa.Integer), sa.column('token_seguimiento', sa.String))
    for (reparacion_id,) in conexion.execute(sa.select(reparaciones.c.id)).fetchall():
        conexion.execute(
            reparaciones.update()
            .where(reparaciones.c.id == reparacion_id)
            .values(token_seguimiento=secrets.token_urlsafe(16))
        )

    with op.batch_alter_table('reparaciones') as batch:
        batch.alter_column('token_seguimiento', existing_type=sa.String(length=32), nullable=False)
        batch.create_unique_constraint('uq_reparaciones_token_seguimiento', ['token_seguimiento'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('reparaciones') as batch:
        batch.drop_constraint('uq_reparaciones_token_seguimiento', type_='unique')
        batch.drop_column('presupuesto_aprobado_at')
        batch.drop_column('token_seguimiento')
