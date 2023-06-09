"""init

Revision ID: 05ed70788c4d
Revises: 
Create Date: 2023-04-28 13:07:16.797750

"""
import sqlalchemy
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core.db import models
from src.core.security import hash_password

# revision identifiers, used by Alembic.
revision = "05ed70788c4d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pokemon",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("type_1", sa.String(), nullable=True),
        sa.Column("type_2", sa.String(), nullable=True),
        sa.Column("total", sa.Integer(), nullable=True),
        sa.Column("hp", sa.Integer(), nullable=True),
        sa.Column("attack", sa.Integer(), nullable=True),
        sa.Column("defense", sa.Integer(), nullable=True),
        sa.Column("sp_atk", sa.Integer(), nullable=True),
        sa.Column("sp_def", sa.Integer(), nullable=True),
        sa.Column("speed", sa.Integer(), nullable=True),
        sa.Column("generation", sa.Integer(), nullable=True),
        sa.Column("legendary", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pokemon")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )

    session = Session(bind=op.get_bind())
    # do initial data migration
    with open("alembic/seeds/pokemon.sql") as file:
        escaped_sql = sqlalchemy.text(file.read())
        session.execute(escaped_sql)

    session.commit()

    if settings().environment != "production":
        # create some users
        users = [
            models.User(
                password=hash_password("12345"),
                first_name="John",
                last_name="Doe",
                email="john.doe@petal.com",
            )
        ]

        session.add_all(users)
        session.flush()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    op.drop_table("pokemon")
    # ### end Alembic commands ###
