# Unlearning to Rest – Home Deployment Runbook

Reference steps for bringing the study environment back online after a shutdown. This assumes the backend and Ollama run on the home workstation and the frontend is hosted on Netlify.

## 1. Prerequisites
- Tailscale logged in on the workstation (`tailscale status` should show the machine connected).
- Python virtual environment already created at `venv/` with dependencies installed (`pip install -r backend/requirements.txt`).
- Ollama installed and the required models pulled (`ollama list`).

## 2. Start Ollama
```bash
ollama serve > logs/ollama.log 2>&1 &
```
- If you previously used `start_optimized.sh`, remember it will try to stop any running Ollama instance before launching; use that script instead if you want the combined startup.

## 3. Launch the Flask API (Gunicorn)
```bash
source venv/bin/activate
export OLLAMA_HOST=http://localhost:11434
export CORS_ORIGINS=https://<your-netlify-site>.netlify.app
export PORT=5000
export LOG_LEVEL=INFO
cd backend
exec gunicorn -w 4 -b 0.0.0.0:${PORT} --timeout 120 --access-logfile ../logs/access.log --error-logfile ../logs/error.log backend.app:create_app()
```
- You can substitute `python app.py` for quick testing, but keep Gunicorn for concurrent users.

## 4. Enable Tailscale Funnel
```bash
sudo tailscale serve reset
sudo tailscale funnel 5000
```
- `tailscale serve status` shows the active funnel URL. Note the HTTPS address; it should match the Netlify `API_BASE_URL` setting.

## 5. Verify Backend Health
```bash
curl http://localhost:5000/health
curl https://<funnel-url>/health
```
Both commands should return the JSON health payload.

## 6. Netlify Configuration
- Build command: `echo "window.ENV={API_BASE_URL:'$API_BASE_URL'};" > env.js`
- Publish directory: `frontend`
- Environment variable `API_BASE_URL` set to the current funnel URL (e.g., `https://<tailnet-host>.ts.net`). Update this if the funnel host name changes.

## 7. Frontend Check
- Visit the Netlify site and confirm login works.
- Browser Network tab should show API calls pointing at the funnel domain (no `/api/...` 404s).

## 8. Logs
- API: `tail -f logs/error.log logs/access.log`
- Ollama: `tail -f logs/ollama.log`

## 9. Exporting Conversation Data
- Admin export endpoint: `curl https://<funnel-url>/admin/export -o export.json`
- Direct SQLite access: `sqlite3 data/study.db` then `SELECT * FROM messages;`

## 10. Shutdown Procedure
1. Stop Gunicorn (Ctrl+C or terminate the process).
2. `sudo tailscale serve reset` to close the public funnel.
3. Stop the background `ollama serve` process if it is still running (`pkill ollama`).

Keep this file updated as you adjust the deployment process.
