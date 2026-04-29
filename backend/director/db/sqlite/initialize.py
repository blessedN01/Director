import sqlite3
import os

# SQL to create the sessions table
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    video_id TEXT,
    collection_id TEXT,
    created_at INTEGER,
    updated_at INTEGER,
    metadata JSON
)
"""

# SQL to create the conversations table
CREATE_CONVERSATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    session_id TEXT,
    conv_id TEXT,
    msg_id TEXT PRIMARY KEY,
    msg_type TEXT,
    agents JSON,
    actions JSON,
    content JSON,
    status TEXT,
    created_at INTEGER,
    updated_at INTEGER,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
)
"""

# SQL to create the context_messages table
CREATE_CONTEXT_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS context_messages (
    session_id TEXT PRIMARY KEY,
    context_data JSON,
    created_at INTEGER,
    updated_at INTEGER,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
)
"""

# SQL to create the collections table
CREATE_COLLECTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    metadata JSON
)
"""

# SQL to create the assets table
CREATE_ASSETS_TABLE = """
CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- 'video', 'audio', 'image'
    file_path TEXT, -- local file path for local implementation
    url TEXT, -- for generated URLs or external links
    metadata JSON, -- duration, size, format, etc.
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
)
"""

# SQL to create the asset_transcripts table
CREATE_TRANSCRIPTS_TABLE = """
CREATE TABLE IF NOT EXISTS asset_transcripts (
    asset_id TEXT PRIMARY KEY,
    transcript_text TEXT,
    transcript_json JSON, -- full transcript with timestamps
    language TEXT DEFAULT 'en',
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
)
"""

# SQL to create the asset_indexes table for search
CREATE_INDEXES_TABLE = """
CREATE TABLE IF NOT EXISTS asset_indexes (
    id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    index_type TEXT NOT NULL, -- 'spoken_word', 'scene', 'semantic'
    index_data JSON, -- embedding vectors, scene data, etc.
    created_at INTEGER NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
)
"""


def initialize_sqlite(db_name="director.db"):
    """Initialize the SQLite database by creating the necessary tables."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(CREATE_SESSIONS_TABLE)
    cursor.execute(CREATE_CONVERSATIONS_TABLE)
    cursor.execute(CREATE_CONTEXT_MESSAGES_TABLE)
    cursor.execute(CREATE_COLLECTIONS_TABLE)
    cursor.execute(CREATE_ASSETS_TABLE)
    cursor.execute(CREATE_TRANSCRIPTS_TABLE)
    cursor.execute(CREATE_INDEXES_TABLE)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    db_path = os.getenv("SQLITE_DB_PATH", "director.db")
    initialize_sqlite(db_path)
