import requests

API_URL = "https://support-desk-assistant-1.onrender.com/api/v1/rag/query"

print("Type your message. Ctrl+C to exit.\n")

while True:
    q = input("> ").strip()
    if not q:
        continue

    r = requests.post(API_URL, json={"query": q}, timeout=60)
    if r.status_code != 200:
        print(f"[{r.status_code}] {r.text}\n")
        continue

    data = r.json()
    print("\n" + (data.get("answer") or "No answer") + "\n")
