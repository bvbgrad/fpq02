"""Add User role, add FPQ person and photo structure

Revision ID: 90deb09f0ba9
Revises: ce4e5b1467ca
Create Date: 2021-01-10 04:20:02.949767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90deb09f0ba9'
down_revision = 'ce4e5b1467ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('person',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('surname', sa.String(), nullable=True),
    sa.Column('given_names', sa.String(), nullable=True),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('year_born', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photo',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('PersonIdFK', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['PersonIdFK'], ['person.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('filename')
    )
    op.add_column('user', sa.Column('role', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    op.drop_table('photo')
    op.drop_table('person')
    # ### end Alembic commands ###
