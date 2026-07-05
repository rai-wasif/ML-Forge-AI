$ErrorActionPreference = "Continue"

Write-Host "Docker services"
docker ps --filter "name=mlforge" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host ""
Write-Host "Qdrant health"
curl.exe -s http://localhost:6333/collections

Write-Host ""
Write-Host "MLflow health"
curl.exe -s http://localhost:5000/health
