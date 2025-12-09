"""
End-to-End Integration Test for Support Desk Assistant.

This test validates the COMPLETE workflow from ticket creation to feedback:
1. Submit a ticket via API
2. AI processes ticket (RAG + Summarization)
3. Ticket is saved to database
4. Retrieve ticket from database
5. Submit feedback on ticket
6. Verify feedback is stored

Uses REAL services:
- OpenAI API for AI processing
- Pinecone for vector search
- SQLite database for persistence
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.db.connection import SessionLocal
from app.infrastructure.db.models import Ticket
from app.infrastructure.repositories import ticket_repository


class TestEndToEnd:
    """Complete end-to-end workflow test."""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        return TestClient(app)

    @pytest.fixture(autouse=True)
    def clean_db_before_test(self):
        """Clean database before test to ensure clean state."""
        session = SessionLocal()
        try:
            session.query(Ticket).delete()
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()
        
        yield

    @pytest.mark.integration
    def test_complete_ticket_workflow_end_to_end(self, client):
        """
        Test COMPLETE support desk workflow end-to-end.
        
        Workflow:
        1. User submits support ticket
        2. AI agent processes ticket (RAG query + summarization)
        3. Agent decides action (reply or escalate)
        4. Ticket saved to database with AI results
        5. User retrieves ticket list
        6. User views specific ticket details
        7. User submits feedback (correct/incorrect)
        8. Feedback is saved to database
        9. System can retrieve ticket with feedback
        
        This tests:
        - POST /api/v1/tickets/agent (AI processing)
        - GET /api/v1/tickets (list tickets)
        - POST /api/v1/tickets/feedback (submit feedback)
        - Database persistence across operations
        - Real OpenAI API integration
        - Real Pinecone vector search
        - Complete data flow
        """
        print("\n" + "="*70)
        print("STARTING END-TO-END TEST: Complete Support Desk Workflow")
        print("="*70)

        # =================================================================
        # STEP 1: User submits a support ticket
        # =================================================================
        print("\n[STEP 1] User submits support ticket...")
        
        ticket_text = "How do I reset my password? I forgot it and can't login."
        
        payload = {
            "ticket": ticket_text
        }
        
        response = client.post("/api/v1/tickets/agent", json=payload)
        
        # Assert submission successful
        assert response.status_code == 200, f"Ticket submission failed: {response.text}"
        
        ticket_data = response.json()
        ticket_id = ticket_data["id"]
        
        print(f"   ✅ Ticket submitted successfully")
        print(f"   📝 Ticket ID: {ticket_id}")
        print(f"   💬 Original text: {ticket_text}")
        
        # Assert response has required fields
        assert "id" in ticket_data
        assert "action" in ticket_data
        assert "reply" in ticket_data
        assert "tags" in ticket_data
        assert "reason" in ticket_data
        
        print(f"   🤖 AI Action: {ticket_data['action']}")
        print(f"   🏷️  AI Tags: {ticket_data['tags']}")
        
        # =================================================================
        # STEP 2: Verify AI processing worked correctly
        # =================================================================
        print("\n[STEP 2] Verifying AI processing...")
        
        # Action should be either 'reply' or 'escalate'
        assert ticket_data["action"] in ["reply", "escalate"], \
            f"Invalid action: {ticket_data['action']}"
        
        # Tags should be a list
        assert isinstance(ticket_data["tags"], list), "Tags should be a list"
        assert len(ticket_data["tags"]) > 0, "Should have at least one tag"
        
        # Reason should explain the decision
        assert ticket_data["reason"] is not None
        assert len(ticket_data["reason"]) > 0
        
        # If action is reply, should have a reply
        if ticket_data["action"] == "reply":
            assert ticket_data["reply"] is not None
            assert len(ticket_data["reply"]) > 0
            print(f"   ✅ AI generated reply: {ticket_data['reply'][:100]}...")
        else:
            print(f"   ✅ AI escalated ticket: {ticket_data['reason']}")
        
        print(f"   ✅ AI processing validated")

        # =================================================================
        # STEP 3: Verify ticket was saved to database
        # =================================================================
        print("\n[STEP 3] Verifying database persistence...")
        
        session = SessionLocal()
        try:
            db_ticket = ticket_repository.get_ticket(db=session, ticket_id=ticket_id)
            
            assert db_ticket is not None, "Ticket not found in database"
            assert db_ticket.id == ticket_id
            assert db_ticket.text == ticket_text
            assert db_ticket.action == ticket_data["action"]
            assert db_ticket.reply == ticket_data["reply"]
            assert db_ticket.reason == ticket_data["reason"]
            
            # Tags stored as comma-separated string in DB
            expected_tags = ",".join(ticket_data["tags"])
            assert db_ticket.tags == expected_tags
            
            print(f"   ✅ Ticket found in database")
            print(f"   💾 Database ID: {db_ticket.id}")
            print(f"   📅 Created at: {db_ticket.created_at}")
            
        finally:
            session.close()

        # =================================================================
        # STEP 4: User retrieves list of tickets
        # =================================================================
        print("\n[STEP 4] User retrieves ticket list...")
        
        response = client.get("/api/v1/tickets")
        
        assert response.status_code == 200
        tickets_list = response.json()
        
        assert isinstance(tickets_list, list)
        assert len(tickets_list) == 1, f"Expected 1 ticket, found {len(tickets_list)}"
        
        # Verify our ticket is in the list
        listed_ticket = tickets_list[0]
        assert listed_ticket["id"] == ticket_id
        assert listed_ticket["text"] == ticket_text
        
        print(f"   ✅ Retrieved {len(tickets_list)} ticket(s)")
        print(f"   📋 Ticket #{listed_ticket['id']}: {listed_ticket['text'][:50]}...")

        # =================================================================
        # STEP 5: User submits feedback on the ticket
        # =================================================================
        print("\n[STEP 5] User submits feedback...")
        
        feedback_payload = {
            "ticket_id": ticket_id,
            "human_label": "correct"
        }
        
        response = client.post("/api/v1/tickets/feedback", json=feedback_payload)
        
        assert response.status_code == 200
        feedback_response = response.json()
        
        assert feedback_response["id"] == ticket_id
        assert feedback_response["human_label"] == "correct"
        
        print(f"   ✅ Feedback submitted successfully")
        print(f"   👍 Human label: {feedback_response['human_label']}")

        # =================================================================
        # STEP 6: Verify feedback was saved to database
        # =================================================================
        print("\n[STEP 6] Verifying feedback persistence...")
        
        session = SessionLocal()
        try:
            db_ticket = ticket_repository.get_ticket(db=session, ticket_id=ticket_id)
            
            assert db_ticket is not None
            assert db_ticket.human_label == "correct"
            
            print(f"   ✅ Feedback stored in database")
            print(f"   👤 Human label: {db_ticket.human_label}")
            
        finally:
            session.close()

        # =================================================================
        # STEP 7: Verify complete ticket data integrity
        # =================================================================
        print("\n[STEP 7] Final data integrity check...")
        
        session = SessionLocal()
        try:
            final_ticket = ticket_repository.get_ticket(db=session, ticket_id=ticket_id)
            
            # Verify all fields are correct
            assert final_ticket.id == ticket_id
            assert final_ticket.text == ticket_text
            assert final_ticket.action in ["reply", "escalate"]
            assert final_ticket.tags is not None
            assert final_ticket.reason is not None
            assert final_ticket.human_label == "correct"
            assert final_ticket.created_at is not None
            
            print(f"   ✅ All data fields verified")
            print(f"   📊 Final ticket state:")
            print(f"      - ID: {final_ticket.id}")
            print(f"      - Text: {final_ticket.text[:50]}...")
            print(f"      - Action: {final_ticket.action}")
            print(f"      - Tags: {final_ticket.tags}")
            print(f"      - Human Label: {final_ticket.human_label}")
            print(f"      - Created: {final_ticket.created_at}")
            
        finally:
            session.close()

        # =================================================================
        # TEST COMPLETE
        # =================================================================
        print("\n" + "="*70)
        print("✅ END-TO-END TEST PASSED!")
        print("="*70)
        print("\nWorkflow Summary:")
        print("  1. ✅ Ticket submitted via API")
        print("  2. ✅ AI processed ticket (OpenAI + Pinecone)")
        print("  3. ✅ Ticket saved to database")
        print("  4. ✅ Ticket retrieved from list")
        print("  5. ✅ Feedback submitted")
        print("  6. ✅ Feedback persisted to database")
        print("  7. ✅ Data integrity verified")
        print("\n🎉 COMPLETE SUPPORT DESK WORKFLOW VALIDATED!")
        print("="*70 + "\n")

    @pytest.mark.integration
    def test_health_check_endpoint(self, client):
        """
        Test the health check endpoint.
        
        Simple test to verify app is running and responding.
        """
        print("\n[HEALTH CHECK] Testing /health endpoint...")
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        
        print(f"   ✅ Health check passed")
        print(f"   💚 Status: {data['status']}")
        print(f"   📦 Version: {data['version']}")
