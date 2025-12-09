# Database Access Guide

## Problem: "Database is Locked" Error

When trying to open `data/test_support.db` in a SQLite browser, you may encounter a "database is locked" error. This happens because Python tests or applications may still have active connections to the database.

## Solutions

### Solution 1: Run the Close Database Script (Recommended)

After running tests, execute this script to forcefully close all database connections:

```bash
python3 close_db.py
```

This script:
- Closes all SQLAlchemy sessions
- Checkpoints and closes WAL files
- Forces garbage collection
- Makes the database safe to open in external tools

### Solution 2: Restart VS Code

If the database is still locked, VS Code's Python extension (Pylance) might be holding it open:

1. Close all Python files in VS Code
2. Reload VS Code window: `Ctrl+Shift+P` → "Developer: Reload Window"
3. Or fully restart VS Code

### Solution 3: Manual Cleanup

If neither solution works, manually check for processes:

```bash
# Find processes using the database
lsof data/test_support.db

# Or use fuser
fuser data/test_support.db

# Kill the process if needed (replace PID with actual process ID)
kill -9 <PID>
```

## Prevention: Test Improvements

The test file `tests/integration/test_database_integration.py` has been updated with:

1. **NullPool**: Disables connection pooling for SQLite
2. **close_all_sessions()**: Closes all active sessions after tests
3. **Garbage collection**: Forces Python to free database handles
4. **pytest_sessionfinish hook**: Runs cleanup after all tests complete

## Usage Workflow

**Recommended workflow when working with the database:**

1. Run your tests:
   ```bash
   pytest tests/integration/test_database_integration.py
   ```

2. Close all connections:
   ```bash
   python3 close_db.py
   ```

3. Open database in SQLite browser:
   - The database file should now be accessible
   - No "database is locked" errors

## Technical Details

SQLite uses file-level locking. When SQLAlchemy or any Python process opens the database:
- A lock is acquired
- The lock persists until the connection is explicitly closed
- Connection pooling can keep connections alive even after code finishes
- WAL (Write-Ahead Logging) mode creates additional lock files

The `NullPool` strategy ensures no connections are kept in a pool, and our cleanup scripts ensure all connections are properly closed.
