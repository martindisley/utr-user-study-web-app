# Unlearning to Rest User Study Web App

A web application for conducting user studies with LLM models (Llama 3.2:3b and UnlearningToRest).

## Project Overview

This application allows undergraduate design students to participate in an ideation activity using two different language models. The app features:

- Simple email-based session tracking (no passwords)
- Model selection interface
- Chat interface with reset functionality and concept capture panel
- Automatic logging of all interactions
- Admin panel for data export

## Tech Stack

- **Frontend**: Vanilla JavaScript + Tailwind CSS
- **Backend**: Python Flask + SQLAlchemy
- **Database**: SQLite
- **LLM**: Ollama (llama3.2:3b + UnlearningToRest)
- **Deployment**: Local network (SSH accessible)

## Development Status

### ✅ Phase 1: Backend Foundation (Complete)
- [x] Project structure
- [x] Database models
- [x] API endpoints
- [x] Ollama integration
- [x] Configuration management

### 🔄 Phase 2: Frontend Development (Next)
- [ ] Login page
- [ ] Model selection page
- [ ] Chat interface
- [ ] JavaScript modules

### ⏳ Phase 3: Integration & Testing (Pending)
### ⏳ Phase 4: Deployment (Pending)

## Quick Start

### Prerequisites

- Python 3.8+
- Ollama installed and running
- Models pulled: `llama3.2:3b` and `UnlearningToRest`

### 1. Install Backend Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# From the backend directory
python app.py
```

The server will be accessible at `http://<your-machine-ip>:5000`

### 3. Verify Setup

```bash
# Check server health
curl http://localhost:5000/health

# List available models
curl http://localhost:5000/api/models
```

## Project Structure

```
utr-user-study-web-app/
├── backend/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   ├── models.py           # SQLAlchemy models
│   ├── requirements.txt    # Python dependencies
│   └── routes/             # API endpoints
│       ├── auth.py
│       ├── models.py
│       ├── chat.py
│       └── admin.py
├── frontend/               # (Phase 2)
│   ├── index.html
│   ├── select-model.html
│   ├── chat.html
│   └── js/
├── data/                   # SQLite database (gitignored)
├── logs/                   # Application logs (gitignored)
└── .gitignore
```

## API Documentation

See [backend/README.md](backend/README.md) for detailed API documentation.

## Configuration

The app can be configured via environment variables:

```bash
OLLAMA_HOST=http://localhost:11434  # Ollama server location
DEBUG=false                          # Debug mode
PORT=5000                           # Server port
```

For VM deployment, update `OLLAMA_HOST` to point to the VM's IP address.

## Data Export

Study data can be exported via:
```bash
curl http://localhost:5000/admin/export > study_data.json
```

## Development Notes

- The app binds to `0.0.0.0` for network accessibility
- No authentication/security (controlled lab environment)
- Session IDs are transient; only user associations persist
- Database is automatically initialized on first run

## Next Steps

1. Complete Phase 2: Frontend Development
2. Test end-to-end flow
3. Prepare deployment environment
4. Conduct pilot testing

## License

Internal use only - User study research project.
