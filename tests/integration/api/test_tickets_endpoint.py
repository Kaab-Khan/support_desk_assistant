"""
Integration tests for /api/v1/tickets/agent endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.main import app


class TestTicketsAgentEndpoint:
    """Integration tests for POST /api/v1/tickets/agent endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture(autouse=True)
    def clean_db_before_test(self):
        """Clean database before each test to ensure consistent IDs."""
        from app.infrastructure.db.connection import SessionLocal
        from app.infrastructure.db.models import Ticket
        
        session = SessionLocal()
        try:
            # Delete all tickets and reset auto-increment
            session.query(Ticket).delete()
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()
        
        yield
    
    @pytest.mark.integration
    def test_process_ticket_successfully_real(self, client):
        """
        Test POST /api/v1/tickets/agent with REAL services (OpenAI + Pinecone).
        
        Scenario: Submit a valid ticket, uses real AI to process it.
        
        Expected behavior:
        - Returns 200 status code
        - Response contains ticket ID, action, reply, tags
        - Ticket is saved to database
        
        Note: This calls real OpenAI API - costs money but validates end-to-end.
        """
        # Arrange
        payload = {
            "ticket": "How do I reset my password?"
        }
        
        # Act
        response = client.post("/api/v1/tickets/agent", json=payload)
        
        # Assert - Check response status
        assert response.status_code == 200
        
        # Assert - Check response structure
        data = response.json()
        assert "id" in data
        assert "action" in data
        assert "reply" in data
        assert "tags" in data
        assert "reason" in data
        
        # Assert - ID is positive integer
        assert data["id"] > 0
        assert isinstance(data["id"], int)
        
        # Assert - Action is valid
        assert data["action"] in ["reply", "escalate"]
        
        # Assert - Tags is a list
        assert isinstance(data["tags"], list)
        
        print(f"\n✅ Real ticket processed: ID={data['id']}, Action={data['action']}")

    @pytest.mark.integration
    def test_process_ticket_escalation_scenario(self, client):
        """
        Test POST /api/v1/tickets/agent with topic likely to escalate.
        
        Scenario: Submit a complex/urgent ticket that AI might escalate.
        
        Expected behavior:
        - Returns 200 status code
        - System decides action (reply or escalate)
        - Response is valid
        """
        # Arrange
        payload = {
            "ticket": "URGENT: My account was hacked and I need immediate help!"
        }
        
        # Act
        response = client.post("/api/v1/tickets/agent", json=payload)
        
        # Assert - Check response status
        assert response.status_code == 200
        
        # Assert - Check response content
        data = response.json()
        assert data["id"] > 0
        assert data["action"] in ["reply", "escalate"]
        
        print(f"\n✅ Urgent ticket processed: ID={data['id']}, Action={data['action']}")

    @pytest.mark.integration
    def test_process_ticket_with_invalid_payload(self, client):
        """
        Test POST /api/v1/tickets/agent with invalid payload.
        
        Scenario: Submit request with missing required field.
        
        Expected behavior:
        - Returns 422 status code (validation error)
        - Response contains error details
        """
        # Arrange
        payload = {
            "wrong_field": "This should fail validation"
        }
        
        # Act
        response = client.post("/api/v1/tickets/agent", json=payload)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    @pytest.mark.skip(reason="Skipping, since raising right type error")
    @pytest.mark.integration
    def test_process_ticket_with_empty_ticket_text(self, client):
        """
        Test POST /api/v1/tickets/agent with empty ticket text.
        
        Scenario: Submit ticket with empty string.
        
        Expected behavior:
        - Returns 422 status code (validation error)
        - Empty text should fail validation
        """
        # Arrange
        payload = {
            "ticket": ""
        }
        
        # Act
        response = client.post("/api/v1/tickets/agent", json=payload)
        
        # Assert
        assert response.status_code == 422

    @pytest.mark.integration
    @patch('app.api.v1.endpoints.ticket_repository.update_ticket_feedback')
    @patch('app.api.v1.endpoints.get_db')
    def test_submit_ticket_feedback_successfully(
        self,
        mock_get_db,
        mock_update_ticket_feedback,
        client
    ):
        """
        Test POST /api/v1/tickets/feedback with valid feedback.
        
        Scenario: User submits human feedback (label) for an existing ticket
        to indicate whether the AI agent's response was correct.
        
        Expected behavior:
        - Returns 200 status code
        - Response contains updated ticket with human_label
        - All ticket fields are preserved
        - Ticket includes id, text, action, reply, tags, reason, human_label
        
        Note: This is a mocked test. Real database integration test needed.
        """
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = mock_db_session
        
        # Mock the updated ticket returned by repository
        mock_ticket = Mock()
        mock_ticket.id = 123
        mock_ticket.text = "How do I reset my password?"
        mock_ticket.action = "reply"
        mock_ticket.reply = "Go to Settings > Security > Reset Password."
        mock_ticket.tags = "password,authentication,account"
        mock_ticket.reason = "Generated reply using RAG."
        mock_ticket.created_at = datetime(2024, 1, 15, 10, 30, 0)
        mock_ticket.human_label = "correct"
        
        mock_update_ticket_feedback.return_value = mock_ticket
        
        payload = {
            "ticket_id": 123,
            "human_label": "correct"
        }
        
        # Act
        response = client.post("/api/v1/tickets/feedback", json=payload)
        
        # Assert - Check response status
        assert response.status_code == 200
        
        # Assert - Check response structure
        data = response.json()
        assert "id" in data
        assert "text" in data
        assert "action" in data
        assert "reply" in data
        assert "tags" in data
        assert "reason" in data
        assert "created_at" in data
        assert "human_label" in data
        
        # Assert - Check response content
        assert data["id"] == 123
        assert data["text"] == "How do I reset my password?"
        assert data["action"] == "reply"
        assert data["reply"] == "Go to Settings > Security > Reset Password."
        assert data["tags"] == ["password", "authentication", "account"]  # List, not string
        assert data["reason"] == "Generated reply using RAG."
        assert data["human_label"] == "correct"
        
        # Assert - Verify repository was called correctly
        mock_update_ticket_feedback.assert_called_once()
        call_kwargs = mock_update_ticket_feedback.call_args.kwargs
        assert call_kwargs["ticket_id"] == 123
        assert call_kwargs["human_label"] == "correct"

    @pytest.mark.integration
    @patch('app.api.v1.endpoints.ticket_repository.list_tickets')
    @patch('app.api.v1.endpoints.get_db')
    def test_list_tickets_successfully(
        self,
        mock_get_db,
        mock_list_tickets,
        client
    ):
        """
        Test GET /api/v1/tickets with default pagination.
        
        Scenario: User requests list of tickets without specifying pagination.
        
        Expected behavior:
        - Returns 200 status code
        - Response is a list of tickets
        - Each ticket has correct structure (id, text, action, reply, tags, etc.)
        - Uses default pagination (skip=0, limit=50)
        """
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = mock_db_session
        
        # Mock tickets returned by repository
        mock_ticket1 = Mock()
        mock_ticket1.id = 1
        mock_ticket1.text = "How do I reset my password?"
        mock_ticket1.action = "reply"
        mock_ticket1.reply = "Go to Settings > Security."
        mock_ticket1.tags = "password,authentication"
        mock_ticket1.reason = "Generated reply using RAG."
        mock_ticket1.created_at = datetime(2024, 1, 15, 10, 30, 0)
        mock_ticket1.human_label = None
        
        mock_ticket2 = Mock()
        mock_ticket2.id = 2
        mock_ticket2.text = "Billing question"
        mock_ticket2.action = "escalate"
        mock_ticket2.reply = None
        mock_ticket2.tags = "billing,urgent"
        mock_ticket2.reason = "Escalated to human."
        mock_ticket2.created_at = datetime(2024, 1, 15, 11, 0, 0)
        mock_ticket2.human_label = "correct"
        
        mock_list_tickets.return_value = [mock_ticket1, mock_ticket2]
        
        # Act
        response = client.get("/api/v1/tickets")
        
        # Assert - Check response status
        assert response.status_code == 200
        
        # Assert - Check response is a list
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Assert - Check first ticket structure
        ticket1 = data[0]
        assert ticket1["id"] == 1
        assert ticket1["text"] == "How do I reset my password?"
        assert ticket1["action"] == "reply"
        assert ticket1["reply"] == "Go to Settings > Security."
        assert ticket1["tags"] == ["password", "authentication"]  # Converted to list
        assert ticket1["reason"] == "Generated reply using RAG."
        assert ticket1["human_label"] is None
        
        # Assert - Check second ticket
        ticket2 = data[1]
        assert ticket2["id"] == 2
        assert ticket2["action"] == "escalate"
        assert ticket2["reply"] is None
        assert ticket2["tags"] == ["billing", "urgent"]
        assert ticket2["human_label"] == "correct"
        
        # Assert - Verify repository was called with default pagination
        mock_list_tickets.assert_called_once()
        call_kwargs = mock_list_tickets.call_args.kwargs
        assert call_kwargs["skip"] == 0
        assert call_kwargs["limit"] == 50

    @pytest.mark.integration
    @patch('app.api.v1.endpoints.ticket_repository.list_tickets')
    @patch('app.api.v1.endpoints.get_db')
    def test_list_tickets_with_custom_pagination(
        self,
        mock_get_db,
        mock_list_tickets,
        client
    ):
        """
        Test GET /api/v1/tickets with custom pagination parameters.
        
        Scenario: User requests specific page with custom skip/limit.
        
        Expected behavior:
        - Returns 200 status code
        - Respects skip and limit query parameters
        - Repository is called with correct pagination values
        """
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = mock_db_session
        
        # Mock a smaller subset of tickets (page 2)
        mock_ticket = Mock()
        mock_ticket.id = 15
        mock_ticket.text = "Question about API"
        mock_ticket.action = "reply"
        mock_ticket.reply = "Check the documentation."
        mock_ticket.tags = "api,documentation"
        mock_ticket.reason = "Generated reply."
        mock_ticket.created_at = datetime(2024, 1, 16, 9, 0, 0)
        mock_ticket.human_label = None
        
        mock_list_tickets.return_value = [mock_ticket]
        
        # Act - Request page 2 with 10 items per page (skip=10, limit=10)
        response = client.get("/api/v1/tickets?skip=10&limit=10")
        
        # Assert - Check response status
        assert response.status_code == 200
        
        # Assert - Check response
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        
        # Assert - Verify repository was called with custom pagination
        mock_list_tickets.assert_called_once()
        call_kwargs = mock_list_tickets.call_args.kwargs
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 10

    @pytest.mark.integration
    @patch('app.api.v1.endpoints.ticket_repository.list_tickets')
    @patch('app.api.v1.endpoints.get_db')
    def test_list_tickets_empty_database(
        self,
        mock_get_db,
        mock_list_tickets,
        client
    ):
        """
        Test GET /api/v1/tickets when database is empty.
        
        Scenario: User requests tickets but none exist yet.
        
        Expected behavior:
        - Returns 200 status code (not 404)
        - Response is empty list []
        - No errors thrown
        """
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = mock_db_session
        
        # Mock empty result
        mock_list_tickets.return_value = []
        
        # Act
        response = client.get("/api/v1/tickets")
        
        # Assert - Check response status
        assert response.status_code == 200
        
        # Assert - Check response is empty list
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
        assert data == []
        
        # Assert - Repository was still called
        mock_list_tickets.assert_called_once()

    @pytest.mark.integration
    def test_process_ticket_with_wrong_data_type(self, client):
        """
        Test POST /api/v1/tickets/agent with wrong JSON data type for ticket field.
        
        Scenario: API client sends JSON integer instead of JSON string.
        Example: {"ticket": 12345} instead of {"ticket": "Ticket 12345"}
        
        Note: This tests the JSON field TYPE, not the content.
        Users can write "Ticket #12345" as a string - that's valid.
        This catches programming errors in API clients.
        
        Expected behavior:
        - Returns 422 validation error
        - Rejects non-string types
        """
        # Arrange
        payload = {
            "ticket": 12345  # JSON integer type
        }
        
        # Act
        response = client.post("/api/v1/tickets/agent", json=payload)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    def test_submit_ticket_feedback_with_wrong_ticket_id_type(self, client):
        """
        Test POST /api/v1/tickets/feedback with wrong data type for ticket_id.
        
        Scenario: API client sends string instead of integer for ticket_id.
        
        Expected behavior:
        - Returns 422 validation error
        - ticket_id must be integer
        """
        # Arrange
        payload = {
            "ticket_id": "abc",  # String instead of integer
            "human_label": "correct"
        }
        
        # Act
        response = client.post("/api/v1/tickets/feedback", json=payload)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    def test_submit_ticket_feedback_with_missing_fields(self, client):
        """
        Test POST /api/v1/tickets/feedback with missing required fields.
        
        Scenario: API client doesn't send required fields.
        
        Expected behavior:
        - Returns 422 validation error for missing fields
        """
        # Test missing ticket_id
        payload1 = {
            "human_label": "correct"
            # ticket_id missing
        }
        
        response1 = client.post("/api/v1/tickets/feedback", json=payload1)
        assert response1.status_code == 422
        
        # Test missing human_label
        payload2 = {
            "ticket_id": 123
            # human_label missing
        }
        
        response2 = client.post("/api/v1/tickets/feedback", json=payload2)
        assert response2.status_code == 422
