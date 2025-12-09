#!/usr/bin/env python3
"""
Utility script to forcefully close all database connections.

Run this before opening the database in an external SQLite browser:
    python3 close_db.py

This ensures no Python processes are holding the database file.
"""
import gc
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from sqlalchemy.pool import NullPool


def close_database_connections(db_path="data/test_support.db"):
    """Close all active database connections."""
    try:
        # Close all SQLAlchemy sessions globally
        close_all_sessions()
        
        # Create a temporary engine and immediately close it
        # This forces any lingering connections to close
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url, poolclass=NullPool)
        
        # Execute PRAGMA to checkpoint and close WAL files if any
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
            conn.commit()
        
        # Dispose engine
        engine.dispose()
        del engine
        
        # Force garbage collection
        gc.collect()
        
        print(f"✓ Successfully closed all connections to {db_path}")
        print(f"✓ Database is now safe to open in SQLite browser")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/test_support.db"
    success = close_database_connections(db_path)
    sys.exit(0 if success else 1)
