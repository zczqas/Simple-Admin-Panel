"""artist record

Revision ID: 9466838e8e3e
Revises: 5d413acc7a57
Create Date: 2025-03-31 16:29:05.245751

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9466838e8e3e"
down_revision: Union[str, None] = "5d413acc7a57"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TYPE genre_enum AS ENUM ('RNB', 'COUNTRY', 'CLASSIC', 'ROCK', 'JAZZ');
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS artists (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        dob DATE,
        address TEXT,
        first_release_year VARCHAR(4),
        no_of_albums_released INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS music (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        album_name VARCHAR(100),
        genre genre_enum,
        artist_id INTEGER REFERENCES artists(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    op.execute("""
    CREATE TRIGGER update_artists_modtime
    BEFORE UPDATE ON artists
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
    """)

    op.execute("""
    CREATE TRIGGER update_music_modtime
    BEFORE UPDATE ON music
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_music_modtime ON music;")
    op.execute("DROP TRIGGER IF EXISTS update_artists_modtime ON artists;")

    op.execute("DROP TABLE IF EXISTS music;")
    op.execute("DROP TABLE IF EXISTS artists;")

    op.execute("DROP TYPE IF EXISTS genre_enum;")
