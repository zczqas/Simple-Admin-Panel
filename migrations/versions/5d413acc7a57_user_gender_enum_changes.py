"""user gender enum changes

Revision ID: 5d413acc7a57
Revises: 8487ae7d2c38
Create Date: 2025-03-31 16:26:30.995705

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d413acc7a57"
down_revision: Union[str, None] = "8487ae7d2c38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_enum') THEN
            CREATE TYPE gender_enum AS ENUM ('M', 'F', 'O');
        END IF;
    END
    $$;
    """)

    op.execute("""
    ALTER TABLE users 
    ALTER COLUMN gender TYPE gender_enum USING gender::gender_enum;
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE users 
    ALTER COLUMN gender TYPE VARCHAR(10) USING gender::VARCHAR(10);
    """)
