from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d5ed6ace5a06"
down_revision = "c5c15ad77725"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "users",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True
        ),

        sa.Column(
            "username",
            sa.String(50),
            nullable=False,
            unique=True
        ),

        sa.Column(
            "email",
            sa.String(150),
            nullable=False,
            unique=True
        ),

        sa.Column(
            "password_hash",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
            server_default="TECHNICIAN"
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False
        )
    )


def downgrade() -> None:

    op.drop_table("users")