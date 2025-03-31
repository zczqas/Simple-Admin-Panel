"""adding gender column in artist table

Revision ID: fa800a8b5b82
Revises: 9466838e8e3e
Create Date: 2025-03-31 16:46:39.316456

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fa800a8b5b82"
down_revision: Union[str, None] = "9466838e8e3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE artists
    ADD COLUMN gender gender_enum;
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE artists
    DROP COLUMN gender;
    """)
