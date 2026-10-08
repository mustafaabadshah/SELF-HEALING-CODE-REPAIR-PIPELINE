# Run FastAPI backend with uvicorn
$ErrorActionPreference = "Stop"
Write-Host "Starting Self-Healing Code Repair Backend on http://localhost:8001..." -ForegroundColor Green
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
