# Jarvis Web Deployment

This repository now includes a deployable web version of the Jarvis HUD.

## What Gets Deployed

- Web UI: `Jarvis/gui/web/index.html`
- HTTP server/API: `Jarvis_AI/web_app.py`
- Start command: `python Jarvis_AI/web_app.py`
- Health check: `/api/health`

The deployed app supports web-safe commands such as time, date, weather, jokes,
notes, todos, Google search, and YouTube search.

Desktop-only actions such as microphone wake word, text-to-speech, screenshots,
volume control, and opening local Windows apps still belong to the local desktop
assistant and will not work from a cloud URL.

## Deploy On Render

1. Push this project to GitHub.
2. Open Render and create a new Web Service from the repository.
3. Render should detect `render.yaml`. If entering settings manually, use:
   - Environment: `Python`
   - Build command: leave blank
   - Start command: `python Jarvis_AI/web_app.py`
   - Health check path: `/api/health`
4. After deploy finishes, Render will show the public URL, for example:
   `https://jarvis-web.onrender.com`

## Run Locally

```powershell
python Jarvis_AI\web_app.py
```

Then open:

```text
http://localhost:8000
```
