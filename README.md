# PathFinder — Full Working Laptop + Mobile Web App

This package contains a complete runnable student career-guidance prototype:
- Responsive frontend for laptop and mobile browsers
- Python FastAPI backend
- SQLite persistence for assessment reports
- Student profile, multi-interest selection and free-text Other interest
- 8-question knowledge check
- Separate skill self-rating (clearly labelled as self-reported)
- Top career matches and a basic learning roadmap
- FAQ chatbot with source notes and an uncertainty fallback
- Assessment history API

## Run on Windows laptop

1. Install Python 3.10+.
2. Extract this ZIP.
3. Open the extracted `PathFinder_Full_Working_Project` folder in VS Code.
4. Open Terminal in that folder and run:

   `python -m venv .venv`

5. Activate:

   `.venv\\Scripts\\activate`

6. Install:

   `pip install -r requirements.txt`

7. Start the server:

   `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

8. On the laptop open:

   `http://127.0.0.1:8000`

API documentation:

   `http://127.0.0.1:8000/docs`

## Run on mobile using the laptop as server

1. Connect the laptop and phone to the SAME Wi-Fi network.
2. Start the server using the command above.
3. On Windows, open Command Prompt and run `ipconfig`.
4. Find the active Wi-Fi adapter's IPv4 Address (example: `192.168.1.7`).
5. On the phone browser open `http://192.168.1.7:8000` (replace with your laptop's actual IPv4 address).
6. If Windows Firewall asks, allow Python on your private network.

The laptop must stay on and the server must keep running. This is local-network access, not a public internet deployment. If the phone cannot connect, check both devices are on the same Wi-Fi and allow port 8000 through Windows Firewall for Private networks.

## Useful endpoints
- `GET /api/health`
- `GET /api/careers`
- `POST /api/assessment`
- `GET /api/assessment/{id}`
- `POST /api/chat`
- `GET /api/history`

## Important project honesty
The current version is a working rule-based prototype. The FAQ chatbot uses simple keyword matching over a small reviewed FAQ file. It is not a trained LLM, not full RAG and not a validated psychometric test. Do not claim otherwise in your presentation. To add reliable RAG later, prepare an expert-reviewed and dated document library, retrieve relevant passages, display citations, and make the chatbot abstain when sources are weak.

## Privacy
This student prototype stores submitted assessment data in a local SQLite database on the laptop. Use demo names for presentations. Before real student use, add consent, access control, data deletion/export, secure deployment and a privacy policy.
