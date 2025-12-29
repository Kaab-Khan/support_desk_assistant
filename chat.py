import requests

API_URL = "https://support-desk-assistant-1.onrender.com/api/v1/rag/query"

print("Chat with Support Assistant (with conversation memory)")
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
        "conversation_history": conversation_history if conversation_history else None
    }

    r = requests.post(API_URL, json=payload, timeout=60)
    if r.status_code != 200:
        print(f"[{r.status_code}] {r.text}\n")
        continue

    data = r.json()
    answer = data.get("answer") or "No answer"
    print("\n" + answer + "\n")
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": q})
    conversation_history.append({"role": "assistant", "content": answer})
    
    # Keep only last 10 messages (5 turns) to manage memory
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]
