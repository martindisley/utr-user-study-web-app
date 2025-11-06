# Unlearning to Rest User Study Web App

A web application for conducting user studies with LLM models (Llama 3.2:3b and UnlearningToRest).

## Project Overview

This application allows undergraduate design students to participate in an ideation activity using two different language models. The app features:

- Simple email-based session tracking (no passwords)
- **Moodboard creation** for collecting reference images before starting
- Model selection interface
- Chat interface with reset functionality and concept capture panel
- Automatic logging of all interactions
- Admin panel for data export

## Tech Stack

- **Frontend**: Vanilla JavaScript + Tailwind CSS (deployed on Netlify)
- **Backend**: Python Flask + SQLAlchemy + Gunicorn
- **Database**: SQLite
- **LLM**: Hugging Face Inference API (Llama 3.2:3B + UnlearningToRest)
- **Image Generation**: Replicate API
- **Deployment**: Backend on home workstation via Tailscale Funnel, frontend on Netlify

## Quick Start

### Prerequisites

- Python 3.8+
- Hugging Face API token (for LLM access)
- Replicate API token (for image generation)
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

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API tokens:

```bash
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
REPLICATE_API_TOKEN=your_replicate_token_here
```

Get your tokens from:
- Hugging Face: https://huggingface.co/settings/tokens
- Replicate: https://replicate.com/account/api-tokens

### 3. Start the Backend Server

**Development Mode:**
```bash
./run.sh
```

**Production Mode (Recommended for user studies):**
```bash
./start_optimized.sh
```

This starts Flask with Gunicorn (8 workers) for concurrent users.

Or manually with Gunicorn:
```bash
source venv/bin/activate
# Environment variables are loaded from .env file automatically
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 \
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
│       ├── prompts.py
│       ├── images.py
│       ├── moodboard.py    # Moodboard image uploads
│       └── admin.py
├── frontend/
│   ├── index.html          # Login page
│   ├── moodboard.html      # Moodboard creation page
│   ├── select-model.html   # Model selection
│   ├── chat.html           # Chat interface
│   ├── gallery.html        # Generated images
│   └── js/
│       ├── config.js       # Configuration
│       ├── api.js          # API client
│       └── storage.js      # LocalStorage utils
├── data/                   # SQLite database (gitignored)
│   ├── images/             # Generated images
│   └── moodboard/          # User-uploaded reference images
├── logs/                   # Application logs (gitignored)
├── .env                    # Environment variables (gitignored)
├── .env.example            # Environment template
├── setup.sh                # Install dependencies
├── run.sh                  # Start dev server
├── start_optimized.sh      # Start production server
└── .gitignore
```

## Configuration

The app uses environment variables for configuration. These are loaded from a `.env` file:

```bash
HUGGINGFACE_API_TOKEN=your_hf_token   # Required for LLM access
REPLICATE_API_TOKEN=your_token_here   # Required for image generation
DEBUG=false                           # Debug mode
PORT=5000                            # Server port
CORS_ORIGINS=*                        # Allowed CORS origins
```

See `.env.example` for a full template.
```

## API Documentation

### Authentication
- `POST /api/login` - Login with email (creates user if new)

### Moodboard
- `POST /api/moodboard/upload` - Upload reference image
- `GET /api/moodboard/<user_id>` - Get user's moodboard images
- `GET /api/moodboard/image/<image_id>` - Serve moodboard image file
- `DELETE /api/moodboard/image/<image_id>` - Delete specific image
- `DELETE /api/moodboard/clear/<user_id>` - Clear all user's moodboard images

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
HUGGINGFACE_API_TOKEN=your_token     # Hugging Face API token
DEBUG=false                          # Debug mode
PORT=5000                           # Server port
```

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
```

## Shutdown Procedure

1. Stop Gunicorn (Ctrl+C or terminate the process)
2. Reset Tailscale funnel: `sudo tailscale serve reset`

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

### Hugging Face API Errors
```bash
# Verify your API token is set correctly
echo $HUGGINGFACE_API_TOKEN

# Test the API connection
python -c "from huggingface_hub import InferenceClient; client = InferenceClient(token='your_token'); print('Connected!')"
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
