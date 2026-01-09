import requests
import uuid
import os

API_URL = "https://support-desk-assistant-1.onrender.com/api/v1/rag/query"

# Generate unique session ID for this chat session
SESSION_ID = str(uuid.uuid4())

# Get owner key from environment (optional - for unlimited access)
OWNER_KEY = os.getenv("OWNER_KEY", "")

print("Chat with Support Assistant (with conversation memory)")
print(f"Session ID: {SESSION_ID}")
print("Type your message. Type 'clear' to reset conversation. Ctrl+C to exit.\n")

# Maintain conversation history in memory
conversation_history = []

while True:
    q = input("> ").strip()
    if not q:
        continue
    
    # Allow user to clear conversation
    if q.lower() == "clear":
        conversation_history = []
        print("\n[Conversation cleared]\n")
        continue

    # Build request payload with conversation history
    payload = {
        "query": q,
        "session_id": SESSION_ID,
        "conversation_history": conversation_history if conversation_history else None
    }
    
    # Add owner key header if available
    headers = {}
    if OWNER_KEY:
        headers["x-owner-key"] = OWNER_KEY

    r = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    
    # Handle rate limit errors
    if r.status_code == 429:
        error_data = r.json()
        if isinstance(error_data, dict) and "detail" in error_data:
            detail = error_data["detail"]
            if isinstance(detail, dict):
                print(f"\n⚠️  {detail.get('message', 'Rate limit exceeded')}\n")
            else:
                print(f"\n⚠️  {detail}\n")
        else:
            print(f"\n⚠️  Rate limit exceeded. Please try again later.\n")
        continue
    elif r.status_code != 200:
        print(f"[{r.status_code}] {r.text}\n")
        continue

    data = r.json()
    answer = data.get("answer") or "No answer"
    print("\n" + answer + "\n")
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": q})
    conversation_history.append({"role": "assistant", "content": answer})
    
    # Keep only last 20 messages (10 turns) to manage memory
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]