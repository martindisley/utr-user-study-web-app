# Unlearning to Rest User Study - Backend

Backend API for the user study web application.

## Phase 1 Status: ✅ Complete

All backend components have been implemented:
- ✅ Project structure
- ✅ Database models (User, Session, Message)
- ✅ API endpoints (auth, models, chat, admin)
- ✅ Ollama integration
- ✅ Configuration management

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

Create a `.env` file in the project root if you need custom settings:

```bash
OLLAMA_HOST=http://localhost:11434
DEBUG=true
PORT=5000
```

### 4. Run the Server

```bash
# From the backend directory
python app.py
```

The server will start on `http://0.0.0.0:5000` (accessible on local network).

## API Endpoints

### Authentication
- `POST /api/login` - Login with email

### Models
- `GET /api/models` - List available models

### Chat
- `POST /api/session` - Create new chat session
- `POST /api/chat` - Send message and get response
- `POST /api/reset` - Reset session (clear context)

### Admin
- `GET /admin/export` - Export all data as JSON
- `GET /admin/stats` - Get study statistics

### Health Check
- `GET /health` - Server health status

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── database.py         # Database initialization
├── models.py           # SQLAlchemy models
├── requirements.txt    # Python dependencies
└── routes/
    ├── __init__.py
    ├── auth.py         # Authentication routes
    ├── models.py       # Model listing routes
    ├── chat.py         # Chat and session routes
    └── admin.py        # Admin and export routes
```

## Database Schema

### Users
- `id` - Primary key
- `email` - Unique email address
- `created_at` - Timestamp

### Sessions
- `id` - Primary key
- `user_id` - Foreign key to Users
- `model_name` - Model identifier
- `created_at` - Timestamp

### Messages
- `id` - Primary key
- `session_id` - Foreign key to Sessions
- `role` - 'user' or 'assistant'
- `content` - Message text
- `timestamp` - Message timestamp

## Available Models

1. **llama3.2:3b** - Standard Llama 3.2 model
2. **UnlearningToRest** - Custom fine-tuned model

## Next Steps

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Ensure Ollama is running on the machine
- [ ] Test the server: `python app.py`
- [ ] Verify models are available in Ollama
- [ ] Proceed to Phase 2 (Frontend Development)

## Troubleshooting

### Import Errors
The lint errors you see (Flask, SQLAlchemy not resolved) are expected until dependencies are installed. Run:
```bash
pip install -r requirements.txt
```

### Ollama Connection Issues
Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### Database Issues
The database is automatically created on first run in the `data/` directory.
