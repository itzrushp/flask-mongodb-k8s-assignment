# deploy.ps1 - Kubernetes deployment script for Windows PowerShell

function Write-Success {
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host $args
}

function Write-Warning {
    Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline
    Write-Host $args
}

function Write-Error-Custom {
    Write-Host "[ERR] " -ForegroundColor Red -NoNewline
    Write-Host $args
}

# Check prerequisites
Write-Host "`n=== Checking Prerequisites ===" -ForegroundColor Cyan

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "kubectl not found. Please install kubectl."
    exit 1
}
Write-Success "kubectl found"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "docker not found. Please install Docker Desktop."
    exit 1
}
Write-Success "docker found"

if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "minikube not found. Please install minikube."
    exit 1
}
Write-Success "minikube found"

# Verify Minikube is running
Write-Host "`n=== Verifying Minikube Status ===" -ForegroundColor Cyan
$null = minikube status

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Minikube not running. Starting..."
    minikube start --driver=docker --memory=4096 --cpus=2
    Write-Success "Minikube started"
} else {
    Write-Success "Minikube is running"
}

# Enable metrics-server for HPA
Write-Host "`n=== Enabling Metrics Server ===" -ForegroundColor Cyan
minikube addons enable metrics-server
Start-Sleep -Seconds 5

# Apply Kubernetes manifests
Write-Host "`n=== Applying Kubernetes Manifests ===" -ForegroundColor Cyan

$manifests = @(
    "01-namespace.yaml",
    "02-mongodb-secret.yaml",
    "03-mongodb-configmap.yaml",
    "04-mongodb-pv.yaml",
    "05-mongodb-pvc.yaml",
    "06-mongodb-statefulset.yaml",
    "07-mongodb-service.yaml",
    "08-flask-deployment.yaml",
    "09-flask-service.yaml",
    "10-hpa.yaml"
)

foreach ($manifest in $manifests) {
    Write-Host "Applying $manifest..." -ForegroundColor Yellow
    kubectl apply -f $manifest
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Applied $manifest"
    } else {
        Write-Error-Custom "Failed to apply $manifest"
    }
}

# Wait for deployments
Write-Host "`n=== Waiting for Deployments ===" -ForegroundColor Cyan

Write-Warning "Waiting for MongoDB to be ready (this takes 30-60 seconds)..."
kubectl wait --for=condition=ready pod -l app=mongodb -n flask-app --timeout=300s

Write-Warning "Waiting for Flask pods to be ready..."
kubectl wait --for=condition=ready pod -l app=flask-app -n flask-app --timeout=300s

Write-Success "All deployments ready!"

# Display pod status
Write-Host "`n=== Pod Status ===" -ForegroundColor Cyan
kubectl get pods -n flask-app

# Get Flask service info
Write-Host "`n=== Flask Service Access ===" -ForegroundColor Cyan
kubectl get service flask-service -n flask-app

Write-Warning "`nNote: Flask will be accessible via minikube service or port-forward"
Write-Host "To access Flask:"
Write-Host "  Option 1: minikube service flask-service -n flask-app"
Write-Host "  Option 2: kubectl port-forward -n flask-app service/flask-service 5000:5000"

Write-Success "Deployment complete!"
