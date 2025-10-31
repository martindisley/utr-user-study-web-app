# Unlearning to Rest User Study Web App

A web application for conducting user studies with LLM models (Llama 3.2:3b and UnlearningToRest).

## Project Overview

This application allows undergraduate design students to participate in an ideation activity using two different language models. The app features:

- Simple email-based session tracking (no passwords)
- Model selection interface
- Chat interface with reset functionality
- Automatic logging of all interactions
- Admin panel for data export

## Tech Stack

- **Frontend**: Vanilla JavaScript + Tailwind CSS (deployed on Netlify)
- **Backend**: Python Flask + SQLAlchemy + Gunicorn
- **Database**: SQLite
- **LLM**: Ollama (llama3.2:3b + UnlearningToRest)
- **Deployment**: Backend on home workstation via Tailscale Funnel, frontend on Netlify

## Quick Start

### Prerequisites

- Python 3.8+
- Ollama installed and running
- Models pulled: `llama3.2:3b` and `UnlearningToRest`
- Tailscale (for public access via Funnel)

### 1. Install Backend Dependencies

```bash
./setup.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Start Ollama

```bash
ollama serve > logs/ollama.log 2>&1 &
```

### 3. Start the Backend Server

**Development Mode:**
```bash
./run.sh
```

**Production Mode (Recommended for user studies):**
```bash
./start_optimized.sh
```

This starts both Ollama and Flask with Gunicorn (8 workers) for concurrent users.

Or manually with Gunicorn:
```bash
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434
export CORS_ORIGINS=https://<your-netlify-site>.netlify.app
export PORT=5000

cd backend
gunicorn -w 4 -b 0.0.0.0:${PORT} \
  --timeout 120 \
  --access-logfile ../logs/access.log \
  --error-logfile ../logs/error.log \
  backend.app:create_app()
```

### 4. Enable Public Access with Tailscale Funnel

```bash
sudo tailscale serve reset
sudo tailscale funnel 5000
```

Check the funnel URL:
```bash
tailscale serve status
```

### 5. Configure Netlify Frontend

Set the environment variable in Netlify:
- `API_BASE_URL`: Your Tailscale funnel URL (e.g., `https://<tailnet-host>.ts.net`)

Build command:
```bash
echo "window.ENV={API_BASE_URL:'$API_BASE_URL'};" > env.js
```

Publish directory: `frontend`

### 6. Verify Setup

```bash
# Check local server health
curl http://localhost:5000/health

# Check public funnel health
curl https://<funnel-url>/health

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
├── frontend/
│   ├── index.html          # Login page
│   ├── select-model.html   # Model selection
│   ├── chat.html           # Chat interface
│   └── js/
│       ├── config.js       # Configuration
│       ├── api.js          # API client
│       └── storage.js      # LocalStorage utils
├── data/                   # SQLite database (gitignored)
├── logs/                   # Application logs (gitignored)
├── setup.sh                # Install dependencies
├── run.sh                  # Start dev server
├── start_optimized.sh      # Start production server
└── .gitignore
```

## API Documentation

### Authentication
- `POST /api/login` - Login with email (creates user if new)

### Models
- `GET /api/models` - List available models

### Chat
- `POST /api/session` - Create new chat session
- `POST /api/chat` - Send message and get AI response
- `POST /api/reset` - Reset session (creates new session)

### Admin
- `GET /admin/export` - Export all data as JSON
- `GET /admin/stats` - Get study statistics

### Health Check
- `GET /health` - Server health status

For detailed examples, see API endpoint documentation in backend source files.

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
# Via API
curl http://localhost:5000/admin/export > study_data.json

# Or via public funnel
curl https://<funnel-url>/admin/export > study_data.json

# Direct SQLite access
sqlite3 data/study.db "SELECT * FROM messages;"
```

## Monitoring

View logs in real-time:
```bash
# API logs
tail -f logs/error.log logs/access.log

# Ollama logs
tail -f logs/ollama.log
```

## Shutdown Procedure

1. Stop Gunicorn (Ctrl+C or terminate the process)
2. Reset Tailscale funnel: `sudo tailscale serve reset`
3. Stop Ollama: `pkill ollama`

## Development Notes

- The app binds to `0.0.0.0` for network accessibility
- No authentication/security (controlled lab environment)
- Session IDs are transient; only user associations persist
- Database is automatically initialized on first run
- Frontend hosted on Netlify with environment variable for API URL
- Backend accessible via Tailscale Funnel for secure public access

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 5000
lsof -i :5000
kill -9 <PID>
```

### Ollama Not Responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve > logs/ollama.log 2>&1 &
```

### CORS Errors
Ensure `CORS_ORIGINS` environment variable matches your Netlify URL.

## Next Steps

1. ~~Complete Phase 2: Frontend Development~~ ✅
2. ~~Test end-to-end flow~~ ✅
3. ~~Prepare deployment environment~~ ✅
4. Conduct pilot testing
5. Run full user study

## License

Internal use only - User study research project.
