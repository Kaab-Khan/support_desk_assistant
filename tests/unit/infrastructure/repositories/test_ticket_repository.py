"""
Unit tests for ticket_repository.create_ticket() function.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.infrastructure.repositories.ticket_repository import create_ticket
from app.infrastructure.db.models import Ticket


class TestCreateTicket:
    """Test suite for create_ticket() function."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        mock = Mock()
        return mock

    @pytest.mark.unit
    def test_create_ticket_with_all_fields(self, mock_db_session):
        """
        Test create_ticket() with all fields provided.
        
        Scenario: Create a ticket with all optional fields populated
        (text, action, reply, tags, reason, human_label).
        
        Expected behavior:
        - Ticket object is created with all fields
        - Tags list is converted to comma-separated string
        - db.add() is called to add ticket to session
        - db.commit() is called to persist to database
        - db.refresh() is called to reload the ticket with DB-generated values
        - Returns the created Ticket object
        """
        # Arrange
        text = "How do I reset my password?"
        action = "reply"
        reply = "Go to Settings > Security > Reset Password."
        tags = ["password", "authentication", "account"]
        reason = "Generated reply using knowledge base context via RAG."
        human_label = None
        
        # Mock the Ticket object that will be returned
        mock_ticket = Mock(spec=Ticket)
        mock_ticket.id = 123
        mock_ticket.text = text
        mock_ticket.action = action
        mock_ticket.reply = reply
        mock_ticket.tags = "password,authentication,account"
        mock_ticket.reason = reason
        mock_ticket.human_label = human_label
        
        # Configure the mock to capture the ticket that gets created
        created_ticket_instance = None
        
        def capture_add(ticket):
            nonlocal created_ticket_instance
            created_ticket_instance = ticket
        
        mock_db_session.add.side_effect = capture_add
        
        # Mock refresh to set the id on the ticket
        def mock_refresh(ticket):
            ticket.id = 123
        
        mock_db_session.refresh.side_effect = mock_refresh
        
        # Act
        result = create_ticket(
            db=mock_db_session,
            text=text,
            action=action,
            reply=reply,
            tags=tags,
            reason=reason,
            human_label=human_label
        )
        
        # Assert - Check database operations were called in correct order
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Assert - Check the ticket object that was created
        assert created_ticket_instance is not None
        assert isinstance(created_ticket_instance, Ticket)
        assert created_ticket_instance.text == text
        assert created_ticket_instance.action == action
        assert created_ticket_instance.reply == reply
        assert created_ticket_instance.tags == "password,authentication,account"  # List converted to string
        assert created_ticket_instance.reason == reason
        assert created_ticket_instance.human_label == human_label
        
        # Assert - Check the returned ticket
        assert result is created_ticket_instance
        assert result.id == 123

    @pytest.mark.unit
    def test_create_ticket_with_minimal_fields(self, mock_db_session):
        """
        Test create_ticket() with only required field (text).
        
        Scenario: Create a ticket with only the text field,
        all other fields are None/default.
        
        Expected behavior:
        - Ticket object is created with only text
        - All optional fields are None
        - Tags conversion handles None properly
        - Database operations still work correctly
        """
        # Arrange
        text = "I need help with my account."
        
        # Configure the mock to capture the ticket
        created_ticket_instance = None
        
        def capture_add(ticket):
            nonlocal created_ticket_instance
            created_ticket_instance = ticket
        
        mock_db_session.add.side_effect = capture_add
        
        def mock_refresh(ticket):
            ticket.id = 456
        
        mock_db_session.refresh.side_effect = mock_refresh
        
        # Act
        result = create_ticket(
            db=mock_db_session,
            text=text
            # All other parameters use default None
        )
        
        # Assert - Check database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Assert - Check the ticket object
        assert created_ticket_instance is not None
        assert created_ticket_instance.text == text
        assert created_ticket_instance.action is None
        assert created_ticket_instance.reply is None
        assert created_ticket_instance.tags is None  # None tags should stay None
        assert created_ticket_instance.reason is None
        assert created_ticket_instance.human_label is None
        
        # Assert - Check returned ticket
        assert result is created_ticket_instance
        assert result.id == 456

    @pytest.mark.unit
    def test_create_ticket_with_empty_tags_list(self, mock_db_session):
        """
        Test create_ticket() with empty tags list.
        
        Scenario: Create a ticket with tags=[] (empty list).
        
        Expected behavior:
        - Empty list should be converted to empty string ""
        - Database operations work correctly
        - All other fields are handled properly
        """
        # Arrange
        text = "Billing question about recent charges."
        action = "escalate"
        tags = []  # Empty list
        
        # Configure the mock
        created_ticket_instance = None
        
        def capture_add(ticket):
            nonlocal created_ticket_instance
            created_ticket_instance = ticket
        
        mock_db_session.add.side_effect = capture_add
        
        def mock_refresh(ticket):
            ticket.id = 789
        
        mock_db_session.refresh.side_effect = mock_refresh
        
        # Act
        result = create_ticket(
            db=mock_db_session,
            text=text,
            action=action,
            tags=tags
        )
        
        # Assert - Check database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Assert - Check the ticket object
        assert created_ticket_instance is not None
        assert created_ticket_instance.text == text
        assert created_ticket_instance.action == action
        assert created_ticket_instance.tags == ""  # Empty list becomes empty string
        
        # Assert - Check returned ticket
        assert result is created_ticket_instance
        assert result.id == 789

    @pytest.mark.unit
    def test_create_ticket_with_none_tags(self, mock_db_session):
        """
        Test create_ticket() with tags=None explicitly.
        
        Scenario: Create a ticket with tags explicitly set to None.
        
        Expected behavior:
        - None tags should remain None (not converted)
        - Database operations work correctly
        - Differentiates between None and empty list
        """
        # Arrange
        text = "Technical issue with API integration."
        action = "reply"
        reply = "Please check the API documentation."
        tags = None  # Explicitly None
        
        # Configure the mock
        created_ticket_instance = None
        
        def capture_add(ticket):
            nonlocal created_ticket_instance
            created_ticket_instance = ticket
        
        mock_db_session.add.side_effect = capture_add
        
        def mock_refresh(ticket):
            ticket.id = 999
        
        mock_db_session.refresh.side_effect = mock_refresh
        
        # Act
        result = create_ticket(
            db=mock_db_session,
            text=text,
            action=action,
            reply=reply,
            tags=tags
        )
        
        # Assert - Check database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Assert - Check the ticket object
        assert created_ticket_instance is not None
        assert created_ticket_instance.text == text
        assert created_ticket_instance.action == action
        assert created_ticket_instance.reply == reply
        assert created_ticket_instance.tags is None  # None stays None
        
        # Assert - Check returned ticket
        assert result is created_ticket_instance
        assert result.id == 999


class TestGetTicket:
    """Test suite for get_ticket() function."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        mock = Mock()
        return mock

    @pytest.mark.unit
    def test_get_ticket_when_ticket_exists(self, mock_db_session):
        """
        Test get_ticket() when ticket with given ID exists in database.
        
        Scenario: Request a ticket by ID that exists in the database.
        
        Expected behavior:
        - Database is queried for the ticket ID
        - Returns the Ticket object
        - Ticket has all expected attributes
        """
        # Arrange
        ticket_id = 123
        
        # Create a mock ticket that will be returned by the query
        mock_ticket = Mock(spec=Ticket)
        mock_ticket.id = ticket_id
        mock_ticket.text = "How do I reset my password?"
        mock_ticket.action = "reply"
        mock_ticket.reply = "Go to Settings > Security."
        mock_ticket.tags = "password,security"
        mock_ticket.reason = "Generated reply via RAG."
        mock_ticket.human_label = None
        
        # Mock the query chain: db.query(Ticket).filter(...).first()
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_ticket
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        from app.infrastructure.repositories.ticket_repository import get_ticket
        result = get_ticket(db=mock_db_session, ticket_id=ticket_id)
        
        # Assert - Check database query was called correctly
        mock_db_session.query.assert_called_once_with(Ticket)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()
        
        # Assert - Check the returned ticket
        assert result is not None
        assert result.id == ticket_id
        assert result.text == "How do I reset my password?"
        assert result.action == "reply"

    @pytest.mark.unit
    def test_get_ticket_when_ticket_not_found(self, mock_db_session):
        """
        Test get_ticket() when ticket with given ID does not exist.
        
        Scenario: Request a ticket by ID that doesn't exist in the database.
        
        Expected behavior:
        - Database is queried for the ticket ID
        - Returns None (not found)
        - Does not raise an exception
        """
        # Arrange
        ticket_id = 999
        
        # Mock the query chain to return None (not found)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        from app.infrastructure.repositories.ticket_repository import get_ticket
        result = get_ticket(db=mock_db_session, ticket_id=ticket_id)
        
        # Assert - Check database query was called
        mock_db_session.query.assert_called_once_with(Ticket)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()
        
        # Assert - Check result is None
        assert result is None


class TestListTickets:
    """Test suite for list_tickets() function."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        mock = Mock()
        return mock

    @pytest.mark.unit
    def test_list_tickets_with_default_pagination(self, mock_db_session):
        """
        Test list_tickets() with default pagination parameters.
        
        Scenario: Request tickets without specifying skip/limit,
        should use defaults (skip=0, limit=50).
        
        Expected behavior:
        - Database is queried with offset(0) and limit(50)
        - Returns list of Ticket objects
        - List contains multiple tickets
        """
        # Arrange
        # Create mock tickets
        mock_ticket1 = Mock(spec=Ticket)
        mock_ticket1.id = 1
        mock_ticket1.text = "First ticket"
        
        mock_ticket2 = Mock(spec=Ticket)
        mock_ticket2.id = 2
        mock_ticket2.text = "Second ticket"
        
        mock_ticket3 = Mock(spec=Ticket)
        mock_ticket3.id = 3
        mock_ticket3.text = "Third ticket"
        
        # Mock the query chain: db.query(Ticket).offset(...).limit(...).all()
        mock_query = Mock()
        mock_offset = Mock()
        mock_limit = Mock()
        mock_limit.all.return_value = [mock_ticket1, mock_ticket2, mock_ticket3]
        mock_offset.limit.return_value = mock_limit
        mock_query.offset.return_value = mock_offset
        mock_db_session.query.return_value = mock_query
        
        # Act
        from app.infrastructure.repositories.ticket_repository import list_tickets
        result = list_tickets(db=mock_db_session)
        
        # Assert - Check database query with default pagination
        mock_db_session.query.assert_called_once_with(Ticket)
        mock_query.offset.assert_called_once_with(0)  # Default skip
        mock_offset.limit.assert_called_once_with(50)  # Default limit
        mock_limit.all.assert_called_once()
        
        # Assert - Check the returned list
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[2].id == 3

    @pytest.mark.unit
    def test_list_tickets_with_custom_pagination(self, mock_db_session):
        """
        Test list_tickets() with custom pagination parameters.
        
        Scenario: Request tickets with skip=10 and limit=5
        (e.g., page 3 with 5 items per page).
        
        Expected behavior:
        - Database is queried with offset(10) and limit(5)
        - Returns list of Ticket objects
        - Respects the custom pagination parameters
        """
        # Arrange
        skip = 10
        limit = 5
        
        # Create mock tickets for the paginated result
        mock_tickets = []
        for i in range(11, 16):  # IDs 11-15 (5 tickets)
            mock_ticket = Mock(spec=Ticket)
            mock_ticket.id = i
            mock_ticket.text = f"Ticket {i}"
            mock_tickets.append(mock_ticket)
        
        # Mock the query chain
        mock_query = Mock()
        mock_offset = Mock()
        mock_limit_result = Mock()
        mock_limit_result.all.return_value = mock_tickets
        mock_offset.limit.return_value = mock_limit_result
        mock_query.offset.return_value = mock_offset
        mock_db_session.query.return_value = mock_query
        
        # Act
        from app.infrastructure.repositories.ticket_repository import list_tickets
        result = list_tickets(db=mock_db_session, skip=skip, limit=limit)
        
        # Assert - Check database query with custom pagination
        mock_db_session.query.assert_called_once_with(Ticket)
        mock_query.offset.assert_called_once_with(10)
        mock_offset.limit.assert_called_once_with(5)
        mock_limit_result.all.assert_called_once()
        
        # Assert - Check the returned list
        assert isinstance(result, list)
        assert len(result) == 5
        assert result[0].id == 11
        assert result[4].id == 15


class TestUpdateTicketAgentResult:
    """Test suite for update_ticket_agent_result() function."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        mock = Mock()
        return mock

    @pytest.mark.unit
    def test_update_ticket_agent_result_with_all_fields(self, mock_db_session):
        """
        Test update_ticket_agent_result() with all fields provided.
        
        Scenario: Update an existing ticket with agent's complete results
        including action, reply, tags, and reason.
        
        Expected behavior:
        - Ticket is retrieved by ID
        - All fields are updated with new values
        - Tags list is converted to comma-separated string
        - db.commit() is called to persist changes
        - db.refresh() is called to reload the ticket
        - Returns the updated Ticket object
        """
        # Arrange
        ticket_id = 123
        action = "reply"
        reply = "To reset your password, go to Settings > Security."
        tags = ["password", "authentication", "account"]
        reason = "Generated reply using knowledge base context via RAG."
        
        # Mock the existing ticket
        mock_ticket = Mock(spec=Ticket)
        mock_ticket.id = ticket_id
        mock_ticket.text = "How do I reset my password?"
        mock_ticket.action = None  # Before update
        mock_ticket.reply = None   # Before update
        mock_ticket.tags = None    # Before update
        mock_ticket.reason = None  # Before update
        
        # Mock get_ticket to return the existing ticket
        def mock_get_ticket(db, tid):
            if tid == ticket_id:
                return mock_ticket
            return None
        
        # Act
        from app.infrastructure.repositories import ticket_repository
        with patch.object(ticket_repository, 'get_ticket', mock_get_ticket):
            result = ticket_repository.update_ticket_agent_result(
                db=mock_db_session,
                ticket_id=ticket_id,
                action=action,
                reply=reply,
                tags=tags,
                reason=reason
            )
        
        # Assert - Check that fields were updated
        assert mock_ticket.action == action
        assert mock_ticket.reply == reply
        assert mock_ticket.tags == "password,authentication,account"  # List converted
        assert mock_ticket.reason == reason
        
        # Assert - Check database operations were called
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_ticket)
        
        # Assert - Check returned ticket
        assert result is mock_ticket
        assert result.id == ticket_id

    @pytest.mark.unit
    def test_update_ticket_agent_result_with_minimal_fields(self, mock_db_session):
        """
        Test update_ticket_agent_result() with only required fields.
        
        Scenario: Update ticket with action and reply only,
        no tags or reason provided.
        
        Expected behavior:
        - Required fields (action, reply) are updated
        - Optional fields (tags, reason) remain unchanged if not provided
        - Database operations still work correctly
        """
        # Arrange
        ticket_id = 456
        action = "escalate"
        reply = None  # Escalated tickets may have no reply
        
        # Mock existing ticket
        mock_ticket = Mock(spec=Ticket)
        mock_ticket.id = ticket_id
        mock_ticket.text = "Complex billing issue"
        mock_ticket.action = None
        mock_ticket.reply = None
        mock_ticket.tags = None
        mock_ticket.reason = None
        
        def mock_get_ticket(db, tid):
            if tid == ticket_id:
                return mock_ticket
            return None
        
        # Act
        from app.infrastructure.repositories import ticket_repository
        with patch.object(ticket_repository, 'get_ticket', mock_get_ticket):
            result = ticket_repository.update_ticket_agent_result(
                db=mock_db_session,
                ticket_id=ticket_id,
                action=action,
                reply=reply
                # tags and reason not provided
            )
        
        # Assert - Check required fields updated
        assert mock_ticket.action == action
        assert mock_ticket.reply == reply
        
        # Assert - Check optional fields remain None
        assert mock_ticket.tags is None  # Not updated
        assert mock_ticket.reason is None  # Not updated
        
        # Assert - Database operations called
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Assert - Returns the ticket
        assert result is mock_ticket

    @pytest.mark.unit
    def test_update_ticket_agent_result_with_empty_tags_list(self, mock_db_session):
        """
        Test update_ticket_agent_result() with empty tags list.
        
        Scenario: Update ticket with tags=[] (empty list).
        
        Expected behavior:
        - Empty list is converted to empty string ""
        - Other fields are updated correctly
        """
        # Arrange
        ticket_id = 789
        action = "reply"
        reply = "Standard response."
        tags = []  # Empty list
        
        mock_ticket = Mock(spec=Ticket)
        mock_ticket.id = ticket_id
        mock_ticket.action = None
        mock_ticket.reply = None
        mock_ticket.tags = None
        
        def mock_get_ticket(db, tid):
            if tid == ticket_id:
                return mock_ticket
            return None
        
        # Act
        from app.infrastructure.repositories import ticket_repository
        with patch.object(ticket_repository, 'get_ticket', mock_get_ticket):
            result = ticket_repository.update_ticket_agent_result(
                db=mock_db_session,
                ticket_id=ticket_id,
                action=action,
                reply=reply,
                tags=tags
            )
        
        # Assert - Empty list becomes empty string
        assert mock_ticket.tags == ""
        
        # Assert - Other fields updated
        assert mock_ticket.action == action
        assert mock_ticket.reply == reply
        
        # Assert - Database operations called
        mock_db_session.commit.assert_called_once()
        assert result is mock_ticket

    @pytest.mark.unit
    def test_update_ticket_agent_result_when_ticket_not_found(self, mock_db_session):
        """
        Test update_ticket_agent_result() when ticket ID doesn't exist.
        
        Scenario: Try to update a non-existent ticket.
        
        Expected behavior:
        - get_ticket() returns None
        - Function returns None (not found)
        - No database operations attempted (no commit/refresh)
        - No exceptions raised
        """
        # Arrange
        ticket_id = 99999  # Non-existent
        action = "reply"
        reply = "Some reply"
        
        def mock_get_ticket(db, tid):
            return None  # Ticket not found
        
        # Act
        from app.infrastructure.repositories import ticket_repository
        with patch.object(ticket_repository, 'get_ticket', mock_get_ticket):
            result = ticket_repository.update_ticket_agent_result(
                db=mock_db_session,
                ticket_id=ticket_id,
                action=action,
                reply=reply
            )
        
        # Assert - Returns None
        assert result is None
        
        # Assert - No database operations attempted
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()

    @pytest.mark.unit
    def test_update_ticket_agent_result_preserves_other_fields(self, mock_db_session):
        """
        Test that update_ticket_agent_result() preserves fields it doesn't update.
        
        Scenario: Update ticket that already has text, created_at, human_label.
        These fields should remain unchanged.
        
        Expected behavior:
        - Only updates action, reply, tags, reason
        - text, created_at, human_label remain unchanged
        """
        # Arrange
        from datetime import datetime
        ticket_id = 111
        
        # Mock existing ticket with all fields populated
        mock_ticket = Mock(spec=Ticket)
        mock_ticket.id = ticket_id
        mock_ticket.text = "Original ticket text"
        mock_ticket.created_at = datetime(2024, 1, 15, 10, 30, 0)
        mock_ticket.human_label = "correct"
        mock_ticket.action = "old_action"
        mock_ticket.reply = "Old reply"
        mock_ticket.tags = "old,tags"
        mock_ticket.reason = "Old reason"
        
        def mock_get_ticket(db, tid):
            if tid == ticket_id:
                return mock_ticket
            return None
        
        # Act
        from app.infrastructure.repositories import ticket_repository
        with patch.object(ticket_repository, 'get_ticket', mock_get_ticket):
            result = ticket_repository.update_ticket_agent_result(
                db=mock_db_session,
                ticket_id=ticket_id,
                action="new_action",
                reply="New reply",
                tags=["new", "tags"],
                reason="New reason"
            )
        
        # Assert - Updated fields
        assert mock_ticket.action == "new_action"
        assert mock_ticket.reply == "New reply"
        assert mock_ticket.tags == "new,tags"
        assert mock_ticket.reason == "New reason"
        
        # Assert - Preserved fields (unchanged)
        assert mock_ticket.text == "Original ticket text"
        assert mock_ticket.created_at == datetime(2024, 1, 15, 10, 30, 0)
        assert mock_ticket.human_label == "correct"
        
        # Assert - Database operations
        mock_db_session.commit.assert_called_once()
        assert result is mock_ticket
