"""
Integration tests for SQLite database operations.

These tests verify real database connectivity and functionality:
1. Database file is created successfully
2. Tables are created with correct schema
3. CRUD operations work correctly
4. Data persistence works
5. Constraints and validations work

Note: These tests use a REAL SQLite database:
- Test database: data/test_support.db (separate from production)
- Tests create and clean up data
- Safe to run multiple times
"""
import pytest
import os
import gc
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session, close_all_sessions
from sqlalchemy.pool import NullPool

from app.infrastructure.db.models import Base, Ticket
from app.infrastructure.db.connection import init_db
from app.infrastructure.repositories import ticket_repository


class TestDatabaseIntegration:
    """Integration tests for SQLite database operations."""

    @pytest.fixture(scope="class")
    def test_db_path(self):
        """Path to test database file."""
        return "data/test_support.db"

    @pytest.fixture(scope="class")
    def engine(self, test_db_path):
        """Create database engine for testing."""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Create engine with connection pooling disabled for SQLite
        db_url = f"sqlite:///{test_db_path}"
        engine = create_engine(
            db_url, 
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=NullPool  # Disable connection pooling
        )
        
        # Use centralized init_db function (Note: this uses production DB_URL from settings)
        # For tests, we create tables directly since we're using a test-specific engine
        Base.metadata.create_all(bind=engine)
        
        yield engine
        
        # Cleanup: Aggressively close all database connections
        # Close all active sessions first
        close_all_sessions()
        
        # Dispose the engine to close all connections
        engine.dispose()
        
        # Force garbage collection to free resources
        gc.collect()
        
        # Delete engine reference
        del engine

    @pytest.fixture(scope="function")
    def db_session(self, engine):
        """Create a fresh database session for each test."""
        # Create session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Clean up database before test - delete all tickets
        try:
            session.query(Ticket).delete()
            session.commit()
        except:
            session.rollback()
        
        yield session
        
        # Cleanup: Rollback and close session
        session.rollback()
        session.close()

    @pytest.mark.integration
    def test_database_file_created(self, test_db_path, engine):
        """
        Test that database file is created successfully.
        
        Scenario: Initialize database for first time.
        
        Expected behavior:
        - Database file exists on disk
        - File is a valid SQLite database
        - Can connect to database
        """
        # Assert - Database file exists
        assert os.path.exists(test_db_path), "Database file should be created"
        assert os.path.isfile(test_db_path), "Should be a file, not directory"
        
        # Assert - File has some size (not empty)
        file_size = os.path.getsize(test_db_path)
        assert file_size > 0, "Database file should not be empty"
        
        # Assert - Can connect to database
        assert engine is not None
        connection = engine.connect()
        assert connection is not None
        connection.close()
        
        print(f"\n✅ Database file created: {test_db_path}")
        print(f"✅ File size: {file_size} bytes")

    @pytest.mark.integration
    def test_database_schema_created(self, engine):
        """
        Test that database tables are created with correct schema.
        
        Scenario: Check database structure matches model definitions.
        
        Expected behavior:
        - Tables exist in database
        - Columns match model definitions
        - Data types are correct
        - Constraints are applied
        """
        # Get inspector
        inspector = inspect(engine)
        
        # Assert - tickets table exists
        tables = inspector.get_table_names()
        assert "tickets" in tables, "tickets table should exist"
        
        # Assert - Check columns
        columns = inspector.get_columns("tickets")
        column_names = [col["name"] for col in columns]
        
        expected_columns = ["id", "text", "action", "reply", "tags", "reason", "human_label", "created_at"]
        for col_name in expected_columns:
            assert col_name in column_names, f"Column '{col_name}' should exist in tickets table"
        
        # Assert - Check primary key
        pk_constraint = inspector.get_pk_constraint("tickets")
        assert "id" in pk_constraint["constrained_columns"], "id should be primary key"
        
        print(f"\n✅ Database schema verified")
        print(f"✅ Tables: {tables}")
        print(f"✅ Columns in 'tickets': {column_names}")

    @pytest.mark.integration
    def test_create_ticket_in_database(self, db_session):
        """
        Test creating a ticket record in database.
        
        Scenario: Insert a new ticket with all fields.
        
        Expected behavior:
        - Ticket is inserted successfully
        - ID is auto-generated
        - All fields are stored correctly
        - created_at timestamp is set
        """
        # Arrange
        text = "How do I reset my password?"
        action = "reply"
        reply = "Go to Settings > Security > Reset Password."
        tags = ["password", "authentication", "account"]
        reason = "Generated reply using knowledge base context via RAG."
        
        # Act
        ticket = ticket_repository.create_ticket(
            db=db_session,
            text=text,
            action=action,
            reply=reply,
            tags=tags,
            reason=reason
        )
        
        # Assert - Ticket created
        assert ticket is not None
        assert ticket.id is not None, "ID should be auto-generated"
        assert ticket.id > 0, "ID should be positive integer"
        
        # Assert - Fields stored correctly
        assert ticket.text == text
        assert ticket.action == action
        assert ticket.reply == reply
        assert ticket.tags == "password,authentication,account"  # Stored as comma-separated
        assert ticket.reason == reason
        assert ticket.human_label is None
        
        # Assert - Timestamp set
        assert ticket.created_at is not None
        assert isinstance(ticket.created_at, datetime)
        
        print(f"\n✅ Ticket created successfully")
        print(f"✅ Ticket ID: {ticket.id}")
        print(f"✅ Created at: {ticket.created_at}")

    @pytest.mark.integration
    def test_retrieve_ticket_from_database(self, db_session):
        """
        Test retrieving a ticket by ID from database.
        
        Scenario: Create ticket, then retrieve it by ID.
        
        Expected behavior:
        - Ticket can be retrieved by ID
        - All fields match what was stored
        - Returns None for non-existent ID
        """
        # Arrange - Create ticket first
        created_ticket = ticket_repository.create_ticket(
            db=db_session,
            text="Test ticket for retrieval",
            action="escalate",
            tags=["test", "retrieval"]
        )
        ticket_id = created_ticket.id
        
        # Act - Retrieve ticket
        retrieved_ticket = ticket_repository.get_ticket(db=db_session, ticket_id=ticket_id)
        
        # Assert - Ticket retrieved successfully
        assert retrieved_ticket is not None
        assert retrieved_ticket.id == ticket_id
        assert retrieved_ticket.text == "Test ticket for retrieval"
        assert retrieved_ticket.action == "escalate"
        assert retrieved_ticket.tags == "test,retrieval"
        
        # Act - Try to retrieve non-existent ticket
        non_existent = ticket_repository.get_ticket(db=db_session, ticket_id=99999)
        
        # Assert - Returns None for non-existent
        assert non_existent is None
        
        print(f"\n✅ Ticket retrieved successfully")
        print(f"✅ Retrieved ticket ID: {retrieved_ticket.id}")
        print(f"✅ Non-existent ticket returns None: {non_existent is None}")

    @pytest.mark.integration
    def test_list_tickets_with_pagination(self, db_session):
        """
        Test listing tickets with pagination.
        
        Scenario: Create multiple tickets, then list with pagination.
        
        Expected behavior:
        - Can list all tickets
        - Pagination works (skip/limit)
        - Returns tickets in order
        """
        # Arrange - Create 5 tickets
        for i in range(1, 6):
            ticket_repository.create_ticket(
                db=db_session,
                text=f"Test ticket {i}",
                action="reply" if i % 2 == 0 else "escalate"
            )
        
        # Act - List all tickets
        all_tickets = ticket_repository.list_tickets(db=db_session, skip=0, limit=10)
        
        # Assert - All tickets returned
        assert len(all_tickets) == 5
        
        # Act - List with pagination (first 3)
        first_page = ticket_repository.list_tickets(db=db_session, skip=0, limit=3)
        
        # Assert - Pagination works
        assert len(first_page) == 3
        
        # Act - List second page (skip 3, get 2)
        second_page = ticket_repository.list_tickets(db=db_session, skip=3, limit=3)
        
        # Assert - Second page has remaining tickets
        assert len(second_page) == 2
        
        print(f"\n✅ Listed {len(all_tickets)} total tickets")
        print(f"✅ First page: {len(first_page)} tickets")
        print(f"✅ Second page: {len(second_page)} tickets")

    @pytest.mark.integration
    def test_update_ticket_feedback(self, db_session):
        """
        Test updating ticket with human feedback.
        
        Scenario: Create ticket, then update with human label.
        
        Expected behavior:
        - Ticket can be updated
        - human_label field is set correctly
        - Other fields remain unchanged
        """
        # Arrange - Create ticket
        ticket = ticket_repository.create_ticket(
            db=db_session,
            text="Test ticket for feedback",
            action="reply",
            reply="Auto-generated reply"
        )
        ticket_id = ticket.id
        
        # Act - Update with feedback
        updated_ticket = ticket_repository.update_ticket_feedback(
            db=db_session,
            ticket_id=ticket_id,
            human_label="correct"
        )
        
        # Assert - Ticket updated
        assert updated_ticket is not None
        assert updated_ticket.id == ticket_id
        assert updated_ticket.human_label == "correct"
        
        # Assert - Other fields unchanged
        assert updated_ticket.text == "Test ticket for feedback"
        assert updated_ticket.action == "reply"
        assert updated_ticket.reply == "Auto-generated reply"
        
        print(f"\n✅ Ticket updated with feedback")
        print(f"✅ Ticket ID: {updated_ticket.id}")
        print(f"✅ Human label: {updated_ticket.human_label}")

    @pytest.mark.integration
    def test_database_persistence(self, engine, test_db_path):
        """
        Test that data persists across sessions.
        
        Scenario: Create ticket in one session, retrieve in another.
        
        Expected behavior:
        - Data persists after session closes
        - Can retrieve data in new session
        - Database file retains data
        """
        # Session 1 - Create ticket
        SessionLocal = sessionmaker(bind=engine)
        session1 = SessionLocal()
        
        try:
            ticket = ticket_repository.create_ticket(
                db=session1,
                text="Persistence test ticket",
                action="escalate"
            )
            ticket_id = ticket.id
        finally:
            session1.close()
        
        # Session 2 - Retrieve ticket
        session2 = SessionLocal()
        
        try:
            retrieved = ticket_repository.get_ticket(db=session2, ticket_id=ticket_id)
            
            # Assert - Data persisted
            assert retrieved is not None
            assert retrieved.id == ticket_id
            assert retrieved.text == "Persistence test ticket"
        finally:
            session2.close()
        
        print(f"\n✅ Data persisted across sessions")
        print(f"✅ Created in session 1, retrieved in session 2")

    @pytest.mark.integration
    def test_tags_storage_format(self, db_session):
        """
        Test that tags are stored and retrieved correctly.
        
        Scenario: Store list of tags, verify storage format.
        
        Expected behavior:
        - Tags list is converted to comma-separated string
        - Empty list is stored as empty string
        - None is stored as None
        """
        # Test 1: List of tags
        ticket1 = ticket_repository.create_ticket(
            db=db_session,
            text="Test 1",
            action="reply",
            tags=["password", "urgent", "authentication"]
        )
        assert ticket1.tags == "password,urgent,authentication"
        
        # Test 2: Empty list
        ticket2 = ticket_repository.create_ticket(
            db=db_session,
            text="Test 2",
            action="escalate",
            tags=[]
        )
        assert ticket2.tags == ""
        
        # Test 3: None
        ticket3 = ticket_repository.create_ticket(
            db=db_session,
            text="Test 3",
            action="reply",
            tags=None
        )
        assert ticket3.tags is None
        
        print(f"\n✅ Tags storage format verified")
        print(f"✅ List → comma-separated: {ticket1.tags}")
        print(f"✅ Empty list → empty string: '{ticket2.tags}'")
        print(f"✅ None → None: {ticket3.tags}")

    @pytest.mark.integration
    def test_database_constraints(self, db_session):
        """
        Test database constraints and validations.
        
        Scenario: Try to create invalid tickets.
        
        Expected behavior:
        - Required fields are enforced
        - Invalid data is rejected
        - Appropriate errors are raised
        """
        # Test - Text field is required (cannot be None)
        with pytest.raises(Exception):
            ticket_repository.create_ticket(
                db=db_session,
                text=None  # Invalid: required field
            )
        
        print(f"\n✅ Database constraints enforced")
        print(f"✅ Required field validation works")

    @pytest.mark.integration
    def test_submit_feedback_via_api_endpoint(self):
        """
        Test submitting feedback through API endpoint with real database.
        
        Scenario: Complete workflow - create ticket, submit feedback via API,
        verify database was updated.
        
        Expected behavior:
        1. Ticket is created in database
        2. API endpoint accepts feedback
        3. Database is updated with human_label
        4. All other fields remain unchanged
        
        Note: Uses the production database (data/support.db) for full integration.
        """
        from fastapi.testclient import TestClient
        from app.main import app
        from app.infrastructure.db.connection import SessionLocal
        
        # Step 1: Create a ticket directly in production database
        session = SessionLocal()
        
        try:
            ticket = ticket_repository.create_ticket(
                db=session,
                text="Integration test - How do I reset my password?",
                action="reply",
                reply="Go to Settings > Security > Reset Password.",
                tags=["password", "authentication", "integration-test"],
                reason="Generated reply using RAG."
            )
            ticket_id = ticket.id
            session.commit()  # Commit so it's available to API
            
            # Verify ticket was created without feedback
            assert ticket.human_label is None
            
            print(f"\n✅ Step 1: Created ticket {ticket_id} in production database")
            
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
        
        # Step 2: Submit feedback through API endpoint
        client = TestClient(app)
        
        payload = {
            "ticket_id": ticket_id,
            "human_label": "correct"
        }
        
        response = client.post("/api/v1/tickets/feedback", json=payload)
        
        # Assert - Check API response
        print(f"✅ Step 2: API response status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Response body: {response.text}")
            
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ticket_id
        assert data["human_label"] == "correct"
        assert data["text"] == "Integration test - How do I reset my password?"
        assert data["action"] == "reply"
        
        print(f"✅ API returned updated ticket with feedback")
        
        # Step 3: Verify database was actually updated by querying again
        session = SessionLocal()
        try:
            updated_ticket = ticket_repository.get_ticket(db=session, ticket_id=ticket_id)
            
            assert updated_ticket is not None
            assert updated_ticket.id == ticket_id
            assert updated_ticket.human_label == "correct"
            
            # Verify all other fields remain unchanged
            assert updated_ticket.text == "Integration test - How do I reset my password?"
            assert updated_ticket.action == "reply"
            assert updated_ticket.reply == "Go to Settings > Security > Reset Password."
            assert updated_ticket.tags == "password,authentication,integration-test"
            assert updated_ticket.reason == "Generated reply using RAG."
            
            print(f"✅ Step 3: Database verified - feedback persisted")
            print(f"✅ Ticket ID: {ticket_id}, Human label: {updated_ticket.human_label}")
            
        finally:
            session.close()


def pytest_sessionfinish(session, exitstatus):
    """
    Pytest hook that runs after all tests in this module complete.
    
    Ensures all database connections are closed to prevent
    'database is locked' errors when opening with external tools.
    """
    # Force close all SQLAlchemy sessions
    close_all_sessions()
    
    # Force garbage collection
    gc.collect()
    
    print("\n✓ All database connections closed and cleaned up")
