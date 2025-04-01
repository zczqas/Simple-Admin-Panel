"""user role column added

Revision ID: 243362f4bb9b
Revises: fa800a8b5b82
Create Date: 2025-04-01 10:33:59.348134

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "243362f4bb9b"
down_revision: Union[str, None] = "fa800a8b5b82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TYPE user_role_enum AS ENUM ('ADMIN', 'USER');
    """)

    op.execute("""
    ALTER TABLE users
    ADD COLUMN role user_role_enum NOT NULL DEFAULT 'USER';
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE users
    DROP COLUMN role;
    """)

    op.execute("""
    DROP TYPE user_role_enum;
    """)
