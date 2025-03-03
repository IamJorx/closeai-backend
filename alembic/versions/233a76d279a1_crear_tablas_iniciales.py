"""crear tablas iniciales

Revision ID: 233a76d279a1
Revises: 
Create Date: 2025-03-02 21:09:42.885006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '233a76d279a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('archivos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre_archivo', sa.String(), nullable=False),
    sa.Column('fecha_carga', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_archivos_id'), 'archivos', ['id'], unique=False)
    op.create_table('transacciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('archivo_id', sa.Integer(), nullable=False),
    sa.Column('id_transaccion', sa.String(), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('cuenta_origen', sa.String(), nullable=False),
    sa.Column('cuenta_destino', sa.String(), nullable=False),
    sa.Column('monto', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('estado', sa.String(), nullable=False),
    sa.Column('extra_data', sa.JSON(), nullable=True),
    sa.CheckConstraint("estado IN ('Exitosa', 'Fallida')", name='check_estado'),
    sa.ForeignKeyConstraint(['archivo_id'], ['archivos.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transacciones_id'), 'transacciones', ['id'], unique=False)
    op.create_index(op.f('ix_transacciones_id_transaccion'), 'transacciones', ['id_transaccion'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transacciones_id_transaccion'), table_name='transacciones')
    op.drop_index(op.f('ix_transacciones_id'), table_name='transacciones')
    op.drop_table('transacciones')
    op.drop_index(op.f('ix_archivos_id'), table_name='archivos')
    op.drop_table('archivos')
    # ### end Alembic commands ### 