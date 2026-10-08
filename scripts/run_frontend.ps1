# Run Vite frontend dev server
$ErrorActionPreference = "Stop"
Set-Location -Path "$PSScriptRoot\..\frontend"
Write-Host "Starting Vite React Frontend on http://localhost:5174..." -ForegroundColor Green
npm run dev
