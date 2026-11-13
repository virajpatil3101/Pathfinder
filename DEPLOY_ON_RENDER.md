# Deploy PathFinder on Render

This project is a FastAPI web app. The `render.yaml` Blueprint starts Uvicorn on Render's assigned port.

## Deployment outline
1. Create a GitHub repository and upload the contents of this project folder (not the ZIP file itself), keeping the folder structure: `app/main.py`, `data/careers.json`, `data/faqs.json`, `static/index.html`, `requirements.txt`, and `render.yaml`.
2. In Render, choose **New + → Blueprint** and connect the GitHub repository.
3. Review the `pathfinder-career-guidance` service and approve deployment.
4. When deployment finishes, open the `onrender.com` URL shown by Render in Chrome.
5. Check `https://YOUR-SERVICE.onrender.com/api/health`; it should return `{"status":"ok","message":"PathFinder backend is running"}`.

Note: Render free web services may sleep when idle and take some time to wake. On a free instance, the local SQLite database is not persistent and assessment records may be lost after a restart or redeploy. Never store sensitive student information in this demonstration app without adding authentication, consent, and appropriate privacy/security controls.
