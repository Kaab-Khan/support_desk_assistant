"""
Unit tests for TicketAgentService.process_ticket() function.
"""
import pytest
from unittest.mock import Mock, MagicMock
from app.core.workflows.ticket_workflow import TicketAgentService


class TestProcessTicket:
    """Test suite for TicketAgentService.process_ticket() method."""

    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service."""
        mock = Mock()
        return mock

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def ticket_agent_service(self, mock_rag_service):
        """Create TicketAgentService instance with mocked dependencies."""
        return TicketAgentService(
            rag_service=mock_rag_service
        )

    @pytest.mark.unit
    def test_process_ticket_with_successful_rag_reply(
        self,
        ticket_agent_service,
        mock_rag_service,
        mock_db_session,
        monkeypatch
    ):
        """
        Test process_ticket when RAG successfully generates a reply.
        
        Expected behavior:
        - Action should be 'reply'
        - Reply should contain the RAG answer
        - Reason should indicate RAG was used
        - Tags should be extracted from RAG (no longer using Summariser)
        """
        # Arrange
        ticket_text = "How do I reset my password?"
        
        # Mock RAG service response (now includes tags!)
        mock_rag_service.answer.return_value = {
            "answer": "To reset your password, go to Settings > Security > Reset Password.",
            "tags": ["password", "authentication", "account"],
            "confidence": "high",
            "sources": [{"id": "doc1", "metadata": {"source": "user_guide.pdf"}}]
        }
        
        # Mock the ticket_repository.create_ticket function
        mock_ticket = Mock()
        mock_ticket.id = 123
        mock_ticket.action = "reply"
        mock_ticket.reply = "To reset your password, go to Settings > Security > Reset Password."
        mock_ticket.reason = "Generated reply using knowledge base context via RAG."
        
        mock_create_ticket = Mock(return_value=mock_ticket)
        monkeypatch.setattr(
            "app.core.workflows.ticket_workflow.ticket_repository.create_ticket",
            mock_create_ticket
        )
        
        # Act
        result = ticket_agent_service.process_ticket(
            db=mock_db_session,
            text=ticket_text
        )
        
        # Assert
        assert result["id"] == 123
        assert result["action"] == "reply"
        assert result["reply"] == "To reset your password, go to Settings > Security > Reset Password."
        assert result["tags"] == ["password", "authentication", "account"]
        assert "RAG" in result["reason"]
        
        # Verify RAG service was called with correct input
        mock_rag_service.answer.assert_called_once_with(ticket_text)
        
        # Verify ticket was created in database
        mock_create_ticket.assert_called_once()
        call_kwargs = mock_create_ticket.call_args.kwargs
        assert call_kwargs["db"] == mock_db_session
        assert call_kwargs["text"] == ticket_text
        assert call_kwargs["action"] == "reply"
        assert call_kwargs["reply"] == "To reset your password, go to Settings > Security > Reset Password."
        assert call_kwargs["tags"] == ["password", "authentication", "account"]
        assert call_kwargs["human_label"] is None

    @pytest.mark.unit
    def test_process_ticket_when_rag_returns_empty_answer(
        self,
        ticket_agent_service,
        mock_rag_service,
        mock_db_session,
        monkeypatch
    ):
        """
        Test process_ticket when RAG returns empty answer.
        
        Expected behavior:
        - Action should be 'escalate'
        - Reply should be None
        - Reason should indicate escalation to human agent
        - Ticket should still be saved with tags
        """
        # Arrange
        ticket_text = "My account was hacked and I need immediate help!"
        
        # Mock RAG service response (empty answer, but still has tags)
        mock_rag_service.answer.return_value = {
            "answer": "",  # Empty answer
            "tags": ["security", "urgent", "account-compromise"],
            "confidence": "low",
            "sources": []
        }
        
        # Mock the ticket_repository.create_ticket function
        mock_ticket = Mock()
        mock_ticket.id = 456
        mock_ticket.action = "escalate"
        mock_ticket.reply = None
        mock_ticket.reason = "Could not generate automated reply; escalating to human agent."
        
        mock_create_ticket = Mock(return_value=mock_ticket)
        monkeypatch.setattr(
            "app.core.workflows.ticket_workflow.ticket_repository.create_ticket",
            mock_create_ticket
        )
        
        # Act
        result = ticket_agent_service.process_ticket(
            db=mock_db_session,
            text=ticket_text
        )
        
        # Assert
        assert result["id"] == 456
        assert result["action"] == "escalate"
        assert result["reply"] is None
        assert result["tags"] == ["security", "urgent", "account-compromise"]
        assert "escalating" in result["reason"].lower()
        assert "human" in result["reason"].lower()
        
        # Verify RAG service was called
        mock_rag_service.answer.assert_called_once_with(ticket_text)
        
        # Verify ticket was created with escalate action
        mock_create_ticket.assert_called_once()
        call_kwargs = mock_create_ticket.call_args.kwargs
        assert call_kwargs["action"] == "escalate"
        assert call_kwargs["reply"] is None
        assert call_kwargs["tags"] == ["security", "urgent", "account-compromise"]

    @pytest.mark.unit
    def test_process_ticket_when_rag_returns_whitespace_only(
        self,
        ticket_agent_service,
        mock_rag_service,
        mock_db_session,
        monkeypatch
    ):
        """
        Test process_ticket when RAG returns only whitespace.
        
        Expected behavior:
        - Action should be 'escalate' (whitespace is not a valid answer)
        - Reply should be None
        - Reason should indicate escalation to human agent
        """
        # Arrange
        ticket_text = "I need help with a complex billing issue"
        
        # Mock RAG service response (whitespace only)
        mock_rag_service.answer.return_value = {
            "answer": "   \n\t  ",  # Only whitespace
            "tags": ["billing", "payment"],
            "confidence": "low",
            "sources": []
        }
        
        # Mock the ticket_repository.create_ticket function
        mock_ticket = Mock()
        mock_ticket.id = 789
        mock_ticket.action = "escalate"
        mock_ticket.reply = None
        mock_ticket.reason = "Could not generate automated reply; escalating to human agent."
        
        mock_create_ticket = Mock(return_value=mock_ticket)
        monkeypatch.setattr(
            "app.core.workflows.ticket_workflow.ticket_repository.create_ticket",
            mock_create_ticket
        )
        
        # Act
        result = ticket_agent_service.process_ticket(
            db=mock_db_session,
            text=ticket_text
        )
        
        # Assert
        assert result["action"] == "escalate"
        assert result["reply"] is None
        
        # Verify ticket was created with escalate action
        call_kwargs = mock_create_ticket.call_args.kwargs
        assert call_kwargs["action"] == "escalate"
        assert call_kwargs["reply"] is None

    @pytest.mark.unit
    def test_process_ticket_when_rag_returns_insufficient_context(
        self,
        ticket_agent_service,
        mock_rag_service,
        mock_db_session,
        monkeypatch
    ):
        """
        Test process_ticket when RAG returns INSUFFICIENT_CONTEXT marker.
        
        Scenario: RAG determines it cannot answer based on available context.
        The LLM returns the special marker 'INSUFFICIENT_CONTEXT'.
        
        Expected behavior:
        - Action should be 'escalate'
        - Reply should be None
        - Reason should indicate knowledge base lacks information
        """
        # Arrange
        ticket_text = "How do I configure the quantum flux capacitor?"
        
        # Mock RAG service response (insufficient context marker)
        mock_rag_service.answer.return_value = {
            "answer": "INSUFFICIENT_CONTEXT",
            "tags": ["technical", "unknown"],
            "confidence": "low",
            "sources": []
        }
        
        # Mock the ticket_repository.create_ticket function
        mock_ticket = Mock()
        mock_ticket.id = 999
        mock_ticket.action = "escalate"
        mock_ticket.reply = None
        mock_ticket.reason = "Knowledge base lacks sufficient information; escalating to human agent."
        
        mock_create_ticket = Mock(return_value=mock_ticket)
        monkeypatch.setattr(
            "app.core.workflows.ticket_workflow.ticket_repository.create_ticket",
            mock_create_ticket
        )
        
        # Act
        result = ticket_agent_service.process_ticket(
            db=mock_db_session,
            text=ticket_text
        )
        
        # Assert
        assert result["action"] == "escalate"
        assert result["reply"] is None
        assert "knowledge base" in result["reason"].lower()
        assert "insufficient" in result["reason"].lower() or "lacks" in result["reason"].lower()
        
        # Verify RAG service was called
        mock_rag_service.answer.assert_called_once_with(ticket_text)
        
        # Verify ticket was created with escalate action
        call_kwargs = mock_create_ticket.call_args.kwargs
        assert call_kwargs["action"] == "escalate"
        assert call_kwargs["reply"] is None
