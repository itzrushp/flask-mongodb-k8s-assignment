# Flask MongoDB Kubernetes Deployment

A production-ready deployment of a **Python Flask application with MongoDB** on **Kubernetes (Minikube)** featuring **Horizontal Pod Autoscaling (HPA)**, persistent storage, and comprehensive testing.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Docker Image Build & Push](#docker-image-build--push)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [DNS Resolution in Kubernetes](#dns-resolution-in-kubernetes)
8. [Resource Requests & Limits](#resource-requests--limits)
9. [Design Choices](#design-choices)
10. [Testing & Autoscaling](#testing--autoscaling)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This project demonstrates a **complete microservices deployment** combining:

- **Flask REST API** with MongoDB integration
- **MongoDB StatefulSet** with persistent volumes
- **Kubernetes Services** (Headless + LoadBalancer)
- **Horizontal Pod Autoscaler (HPA)** for dynamic scaling
- **Health & Readiness Probes** for pod lifecycle management
- **Kubernetes Secrets** for secure credential management
- **Load testing** with automatic scaling demonstration

**Key Features:**
- ✅ Two Flask replicas (scales to 5 under load)
- ✅ MongoDB with persistent storage (5Gi PVC)
- ✅ CPU-based autoscaling (70% threshold)
- ✅ Pod-to-pod DNS resolution via headless service
- ✅ Health checks for reliable deployments
- ✅ Comprehensive YAML manifests
- ✅ Automated deployment script

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Minikube Cluster                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │  Flask Pod 1     │        │  Flask Pod 2     │         │
│  │  (Running)       │◄──────►│  (Running)       │         │
│  └──────────────────┘        └──────────────────┘         │
│           │                           │                    │
│           └───────────┬───────────────┘                    │
│                       │                                     │
│            ┌──────────▼──────────┐                        │
│            │  flask-service      │                        │
│            │  (LoadBalancer)     │                        │
│            │  Port: 5000:30311   │                        │
│            └─────────────────────┘                        │
│                       │                                     │
│            ┌──────────▼──────────┐                        │
│            │   HPA Controller    │                        │
│            │  (Monitors CPU%)    │                        │
│            │  Scales 2 → 5 pods  │                        │
│            └─────────────────────┘                        │
│                       │                                     │
│            ┌──────────▼──────────┐                        │
│            │    MongoDB Pod      │                        │
│            │  (StatefulSet)      │                        │
│            │  PVC: 5Gi           │                        │
│            └─────────────────────┘                        │
│                       │                                     │
│            ┌──────────▼──────────┐                        │
│            │  mongodb-service    │                        │
│            │  (Headless)         │                        │
│            │  Port: 27017        │                        │
│            └─────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

**System Requirements:**
- Windows, macOS, or Linux
- **Minikube** v1.30+ ([install](https://minikube.sigs.k8s.io/docs/start/))
- **kubectl** v1.25+ ([install](https://kubernetes.io/docs/tasks/tools/))
- **Docker** ([install](https://www.docker.com/products/docker-desktop))
- **Python** 3.8+ (for load testing)
- **Git** (for cloning/version control)

**Resources:**
- CPU: 4 cores (minimum)
- RAM: 6GB (minimum)
- Disk: 20GB free

---

## Project Structure

```
flask-mongodb-app/
├── Dockerfile                    # Flask image definition
├── app.py                        # Flask application
├── requirements.txt              # Python dependencies
├── deploy.ps1                    # Automated deployment script
├── load-test.py                  # Autoscaling load test
├── README.md                     # This file
├── k8s-manifests/                # Kubernetes YAML files
│   ├── 01-namespace.yaml         # Namespace: flask-app
│   ├── 02-mongodb-secret.yaml    # Root credentials
│   ├── 03-mongodb-configmap.yaml # MongoDB config
│   ├── 04-mongodb-pv.yaml        # PersistentVolume
│   ├── 05-mongodb-pvc.yaml       # PersistentVolumeClaim
│   ├── 06-mongodb-statefulset.yaml
│   ├── 07-mongodb-service.yaml   # Headless service
│   ├── 08-flask-deployment.yaml  # Flask replicas
│   ├── 09-flask-service.yaml     # LoadBalancer service
│   └── 10-hpa.yaml               # Horizontal Pod Autoscaler
└── screenshots/                  # Test results & proof
    ├── 01-health-endpoint.png
    ├── 02-data-endpoint.png
    ├── 03-hpa-scaling.png
    ├── 04-pods-scaling.png
    ├── 05-load-test-output.png
    └── 06-kubectl-all.png
```

---

## Docker Image Build & Push

### Step 1: Build the Image

From the project root directory:

```bash
# Build the Flask image
docker build -t <your-registry>/<your-repo>:latest .

# Example:
docker build -t rcoem2022/flask-mongodb-app:latest .
```

**What the Dockerfile does:**
- Starts from `python:3.10-slim` (lightweight base)
- Sets working directory to `/app`
- Copies `requirements.txt` and installs dependencies
- Copies `app.py` (Flask application)
- Exposes port 5000
- Runs Flask in production mode

### Step 2: Log In to Docker Registry

```bash
# Log in to Docker Hub (or your private registry)
docker login

# Enter your username and password when prompted
```

### Step 3: Push the Image

```bash
# Push to registry
docker push rcoem2022/flask-mongodb-app:latest

# Verify (list images on registry)
docker images | grep flask-mongodb-app
```

**Why this registry?**
- Public Docker Hub for easy distribution
- Alternative: Amazon ECR, Google Container Registry, or private registries with authentication

---

## Kubernetes Deployment

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=6g --driver=docker

# (Windows with Hyper-V or VirtualBox)
minikube start --cpus=4 --memory=6g --driver=hyperv
```

### Step 2: Enable Metrics Server

```bash
# Required for HPA to read CPU metrics
minikube addons enable metrics-server

# Verify it's running
kubectl get deployment -n kube-system | grep metrics-server
```

### Step 3: Deploy the Application (Automated)

Navigate to the `k8s-manifests` folder and run the deployment script:

**On PowerShell (Windows):**
```powershell
cd k8s-manifests
./deploy.ps1
```

**On Bash (macOS/Linux):**
```bash
cd k8s-manifests
chmod +x deploy.sh  # Make it executable (if using bash)
./deploy.ps1  # or equivalent bash script
```

**Or manually apply manifests:**
```bash
cd k8s-manifests

kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-mongodb-secret.yaml
kubectl apply -f 03-mongodb-configmap.yaml
kubectl apply -f 04-mongodb-pv.yaml
kubectl apply -f 05-mongodb-pvc.yaml
kubectl apply -f 06-mongodb-statefulset.yaml
kubectl apply -f 07-mongodb-service.yaml
kubectl apply -f 08-flask-deployment.yaml
kubectl apply -f 09-flask-service.yaml
kubectl apply -f 10-hpa.yaml
```

### Step 4: Verify Deployment

```bash
# Check all resources in flask-app namespace
kubectl get all -n flask-app

# Expected output:
# NAME                             READY   STATUS    RESTARTS   AGE
# pod/flask-app-xxxxx              1/1     Running   0          2m
# pod/flask-app-yyyyy              1/1     Running   0          2m
# pod/mongodb-0                    1/1     Running   0          2m
#
# NAME                      TYPE           CLUSTER-IP   ...
# service/flask-service     LoadBalancer   10.x.x.x     ...
# service/mongodb-service   ClusterIP      None         ...
#
# NAME                   READY   UP-TO-DATE   AVAILABLE   AGE
# deployment.apps/flask-app   2/2     2            2          2m
#
# NAME                      DESIRED   CURRENT   READY   AGE
# statefulset.apps/mongodb   1         1         1       2m
#
# NAME                                    REFERENCE              TARGETS    MINPODS   MAXPODS
# horizontalpodautoscaler.apps/flask-hpa  Deployment/flask-app   1%/70%     2         5
```

### Step 5: Access the Application

```bash
# Open the Flask service via Minikube tunnel
minikube service flask-service -n flask-app

# This will print:
# http://127.0.0.1:<port>

# Open this URL in your browser
```

**Alternative: Port-forward**
```bash
# If tunnel doesn't work, use port-forward
kubectl port-forward -n flask-app service/flask-service 5000:5000

# Then access http://localhost:5000
```

---

## DNS Resolution in Kubernetes

### How It Works

Kubernetes includes **CoreDNS**, a DNS server that automatically creates DNS entries for each Service and Pod.

#### 1. **Service DNS Names**

Every Kubernetes Service gets a DNS name in the format:
```
<service-name>.<namespace>.svc.cluster.local
```

**In this deployment:**

- **Flask Service:** `flask-service.flask-app.svc.cluster.local`
  - Resolves to LoadBalancer IP: `10.104.83.141`

- **MongoDB Service (Headless):** `mongodb-service.flask-app.svc.cluster.local`
  - Resolves to individual pod IPs (not load-balanced)
  - Ensures Flask pods always connect to the **same MongoDB instance**

#### 2. **Pod-to-Pod Communication**

When a Flask pod needs to connect to MongoDB:

1. Flask pod calls: `mongodb-service` (short name)
2. CoreDNS resolves it to: `mongodb-service.flask-app.svc.cluster.local`
3. CoreDNS returns the **MongoDB pod IP** (e.g., `10.244.0.4`)
4. Flask pod connects directly to MongoDB on port `27017`

**Example from app.py:**
```python
mongo_host = os.environ.get("MONGO_HOST", "mongodb-service")
# Inside the cluster, this resolves to mongodb-service.flask-app.svc.cluster.local
# which points to mongodb-0 pod IP
```

#### 3. **Headless vs. Regular Services**

| Feature | Headless Service | Regular Service |
|---------|-----------------|-----------------|
| **DNS Name** | Points to individual pod IPs | Points to service IP (load-balanced) |
| **Use Case** | Databases (need stable identity) | Web services (need load balancing) |
| **MongoDB** | ✅ Uses headless (stable pod name) | ❌ Would cause issues |
| **Flask** | ❌ Not needed | ✅ Uses regular (clients load-balanced) |

#### 4. **Testing DNS Resolution**

From inside a Flask pod:
```bash
# Exec into a Flask pod
kubectl exec -it -n flask-app <flask-pod-name> -- /bin/bash

# Inside the pod, test DNS
nslookup mongodb-service
# Returns: 10.244.0.4 (MongoDB pod IP)

nslookup flask-service
# Returns: 10.104.83.141 (Flask service cluster IP)
```

---

## Resource Requests & Limits

### What Are They?

**Requests:** Minimum resources guaranteed to the pod
- Kubernetes scheduler uses this to decide which node to place the pod
- Pod is guaranteed at least this much

**Limits:** Maximum resources allowed
- Pod is throttled (CPU) or killed (memory) if it exceeds this
- Prevents resource hog pods from affecting others

### Configuration in This Project

#### Flask Deployment
```yaml
resources:
  requests:
    cpu: 200m        # 0.2 CPU cores (guaranteed)
    memory: 256Mi    # 256 MB RAM (guaranteed)
  limits:
    cpu: 500m        # 0.5 CPU cores (max)
    memory: 512Mi    # 512 MB RAM (max)
```

**What this means:**
- Kubernetes reserves 200m CPU + 256Mi RAM for each Flask pod
- If CPU goes above 500m, it's throttled (slowed down)
- If memory goes above 512Mi, pod is restarted (OOMKilled)
- HPA watches these metrics and scales based on CPU usage

#### MongoDB StatefulSet
```yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### HPA Configuration

```yaml
# From 10-hpa.yaml
targetCPUUtilizationPercentage: 70
minReplicas: 2
maxReplicas: 5
```

**How HPA uses requests:**
1. HPA reads actual CPU usage (e.g., 350m)
2. Calculates utilization: `(350m / 200m requests) × 100 = 175%`
3. **175% > 70% target** → HPA adds a new pod
4. Now 4 pods × 200m = 800m reserved, usage spreads
5. New utilization: `(350m / 800m) × 100 = 43.75%` → Stable

### Resource Sizing Strategy

**Why 200m/256Mi requests?**
- Minikube has ~6GB available
- 2 Flask pods + 1 MongoDB = 3 × 256Mi = 768Mi (leaves plenty headroom)
- Allows scale-up to 5 pods = 5 × 256Mi = 1.28GB (still safe)

**Why 500m/512Mi limits?**
- Provides burst capacity during load spikes
- Prevents runaway containers
- Still conservative enough for Minikube

---

## Design Choices

### 1. MongoDB as StatefulSet (Not Deployment)

**Choice:** StatefulSet with PersistentVolumeClaim

**Why?**
- **Stable Identity:** Pod name always `mongodb-0`, enabling DNS resolution `mongodb-service` → specific pod
- **Persistent Storage:** Data survives pod restarts (PVC)
- **Ordered Deployment:** Ensures clean startup/shutdown

**Alternative Considered:**
- Simple Deployment with `emptyDir` volume
- **Rejected:** Data would be lost on pod restart; unacceptable for a database

---

### 2. Headless Service for MongoDB

**Choice:** `clusterIP: None` in `07-mongodb-service.yaml`

**Why?**
- Returns **individual pod IP** instead of service IP
- Flask always connects to the **same MongoDB instance**
- Necessary for stateful workloads

**Alternative:**
- Regular ClusterIP service
- **Rejected:** Would load-balance across pods, causing session issues with MongoDB

---

### 3. Kubernetes Secrets for Credentials

**Choice:** Secret resource with base64-encoded username/password

**Why?**
- Credentials not hard-coded in YAML or code
- Can be rotated without redeploying application code
- RBAC can restrict who views secrets
- Better than ConfigMap (which is meant for non-sensitive config)

**Alternative:**
- Hard-coded in `app.py` or YAML
- **Rejected:** Security risk; exposes credentials in version control

---

### 4. Flask Deployment with 2 Replicas + HPA

**Choice:** Deployment with `replicas: 2`, HPA scales `2 → 5`

**Why?**
- **2 replicas:** High availability (if one pod fails, traffic goes to the other)
- **HPA:** Automatically handles load spikes without manual intervention
- **70% CPU threshold:** Balances cost (not over-provisioning) vs. responsiveness

**Alternatives:**
- Single pod: **Rejected** (no HA, single point of failure)
- Static 5 replicas: **Rejected** (wasteful; 3 pods sit idle during normal load)
- No HPA, manual scaling: **Rejected** (not cloud-native, slow to respond)

---

### 5. Separate Namespace (`flask-app`)

**Choice:** Create dedicated namespace for the entire stack

**Why?**
- Isolates resources from system namespace and other applications
- Makes cleanup easier (`kubectl delete namespace flask-app`)
- RBAC policies can be applied per-namespace
- Organizes resources logically

**Alternative:**
- Deploy to `default` namespace
- **Rejected:** Clutters default namespace; harder to manage

---

### 6. Liveness & Readiness Probes

**Choice:** HTTP probes on `/health` and `/ready` endpoints

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
```
- Checks if Flask app is **running** (not crashed)
- If fails 3× in a row → Kubernetes restarts the pod
- Prevents zombie pods

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 2
```
- Checks if Flask **and MongoDB** are healthy
- If fails → Kubernetes removes pod from service (no traffic sent)
- Prevents requests to broken pods

**Alternative:**
- No probes
- **Rejected:** Dead pods keep receiving traffic; poor user experience

---

### 7. Rolling Update Strategy

**Choice:** `type: RollingUpdate` with `maxSurge: 1, maxUnavailable: 0`

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1           # Max 1 extra pod during update
    maxUnavailable: 0     # Never have 0 pods (always available)
```

**Why?**
- When deploying new image, 1 new pod starts while old pod stops
- Ensures **zero downtime** during updates
- Requests smoothly transition to new pod

**Alternative:**
- `Recreate` (kill all → start new)
- **Rejected:** Causes brief downtime; unacceptable for production

---

## Testing & Autoscaling

### Test 1: Database Interaction

**Objective:** Verify Flask can read/write to MongoDB

**Steps:**

1. Access the Flask app:
   ```bash
   minikube service flask-service -n flask-app
   # Opens browser at http://127.0.0.1:<port>
   ```

2. Test `/` endpoint (health check):
   ```bash
   curl http://127.0.0.1:<port>/
   
   # Expected response:
   # {
   #   "current_time": "2025-12-02T06:28:14.889534",
   #   "message": "Welcome to the Flask app!",
   #   "status": "healthy"
   # }
   ```

3. Insert data via `/data` (POST):
   ```bash
   curl -X POST http://127.0.0.1:<port>/data \
     -H "Content-Type: application/json" \
     -d '{"testField":"testValue","timestamp":"2025-12-02T12:00:00"}'
   
   # Expected response (HTTP 201):
   # {
   #   "status": "Data inserted",
   #   "inserted_id": "692e8763732d0cb0d322b549"
   # }
   ```

4. Read data back via `/data` (GET):
   ```bash
   curl http://127.0.0.1:<port>/data
   
   # Expected response (HTTP 200):
   # {
   #   "count": 1,
   #   "data": [
   #     {
   #       "testField": "testValue",
   #       "timestamp": "2025-12-02T12:00:00",
   #       "created_at": "2025-12-02T06:29:55.992740"
   #     }
   #   ]
   # }
   ```

**Results:** ✅ All endpoints respond correctly. MongoDB insert/read operations work end-to-end.

---

### Test 2: Autoscaling Under Load

**Objective:** Verify HPA scales pods when CPU exceeds 70%

**Setup:**

1. Open **Terminal Window A** (monitor HPA):
   ```bash
   kubectl get hpa -n flask-app -w
   
   # Watch for TARGETS and REPLICAS changes
   ```

2. Open **Terminal Window B** (monitor pods):
   ```bash
   kubectl get pods -n flask-app -w
   
   # Watch for new pods being created
   ```

3. Open **Terminal Window C** (run load test):
   ```bash
   python load-test.py
   ```

**Load Test Script:**
```python
# load-test.py
concurrent_requests = 50   # 50 concurrent requests
duration = 60              # Run for 60 seconds
target_url = "http://127.0.0.1:<port>/data"
```

**Load Test Output:**
```
Starting load test: 50 concurrent requests for 60 seconds
Total requests: 7900
Completed in 60.2 seconds
```

**HPA Output During Load (Window A):**
```
NAME       REFERENCE              TARGETS     MINPODS   MAXPODS   REPLICAS
flask-hpa  Deployment/flask-app   1%/70%      2         5         2

# After ~10 seconds (load reaches peak):
flask-hpa  Deployment/flask-app   150%/70%    2         5         2
flask-hpa  Deployment/flask-app   155%/70%    2         5         3
flask-hpa  Deployment/flask-app   155%/70%    2         5         4
```

**Pods Output During Load (Window B):**
```
flask-app-xxxxx  1/1  Running
flask-app-yyyyy  1/1  Running

# New pods created:
flask-app-zzzzz  0/1  ContainerCreating
flask-app-wwwww  0/1  ContainerCreating

# After ~20 seconds:
flask-app-xxxxx  1/1  Running
flask-app-yyyyy  1/1  Running
flask-app-zzzzz  1/1  Running
flask-app-wwwww  1/1  Running
```

**After Load Test Ends (scale-down, ~5 minutes):**
```
# HPA reduces CPU, scales back:
flask-hpa  Deployment/flask-app   20%/70%     2         5         3
flask-hpa  Deployment/flask-app   15%/70%     2         5         2
```

**Results:** ✅ HPA successfully scaled from 2 to 4 pods. Replicas returned to minimum (2) after load stopped.

---

### Issues Encountered & Solutions

#### Issue 1: MongoDB Authentication Failed

**Error:**
```
ERROR:__main__:MongoDB connection failed: Authentication failed., full error: 
{'ok': 0.0, 'errmsg': 'Authentication failed.', 'code': 18, 'codeName': 'AuthenticationFailed'}
```

**Root Cause:**
- Flask app used credentials `admin/admin123`
- MongoDB was initialized with `root/root123`
- Credential mismatch caused auth failure

**Solution:**
- Updated `08-flask-deployment.yaml` to use `root-username` and `root-password` keys from secret
- Ensured both Deployment and StatefulSet reference the same secret

**Fixed env section:**
```yaml
env:
  - name: MONGO_USERNAME
    valueFrom:
      secretKeyRef:
        name: mongodb-secret
        key: root-username
  - name: MONGO_PASSWORD
    valueFrom:
      secretKeyRef:
        name: mongodb-secret
        key: root-password
```

---

#### Issue 2: MongoDB Liveness Probe Failing

**Error:**
```
Warning  Unhealthy  15m (x5 over 16m)  kubelet  Liveness probe failed: /bin/sh: 1: mongo: not found
```

**Root Cause:**
- Liveness probe used `mongo --eval ...` command
- `mongo` CLI client not installed in `mongo:6.0` image
- Probe kept failing, causing pod restarts

**Solution:**
- Removed liveness/readiness probes from MongoDB StatefulSet
- MongoDB starts successfully and remains stable without probes
- Flask side (readiness probe on `/ready`) verifies MongoDB is up

**Result:** MongoDB pod stabilized and stayed Running.

---

#### Issue 3: Metrics Server Delayed (HPA showed "unknown" metrics)

**Error:**
```
$ kubectl get hpa -n flask-app
NAME       REFERENCE              TARGETS     MINPODS   MAXPODS
flask-hpa  Deployment/flask-app   <unknown>   2         5
```

**Root Cause:**
- Metrics server was enabled but hadn't collected metrics yet
- HPA needs ~1-2 minutes of data before scaling

**Solution:**
- Waited 2-3 minutes for metrics-server to populate data
- Retried `kubectl get hpa`
- HPA then showed `1%/70%` and scaled correctly

**Lesson:** Metrics server requires a warmup period; HPA scales only after data is available.

---

## Troubleshooting

### Pod stuck in `Pending`

```bash
# Check why pod can't be scheduled
kubectl describe pod <pod-name> -n flask-app

# Look for: "0/1 nodes available: insufficient memory"
# Solution: Start Minikube with more memory
minikube start --cpus=4 --memory=8g
```

### Pod in `CrashLoopBackOff`

```bash
# View logs to see crash reason
kubectl logs <pod-name> -n flask-app

# Check probe failures
kubectl describe pod <pod-name> -n flask-app | tail -30
```

### Service unreachable

```bash
# Ensure service exists
kubectl get svc -n flask-app

# Try port-forward instead of minikube service
kubectl port-forward -n flask-app service/flask-service 5000:5000
curl http://localhost:5000
```

### Metrics not updating (HPA stuck)

```bash
# Check if metrics-server is running
kubectl get deployment -n kube-system | grep metrics-server

# If not enabled:
minikube addons enable metrics-server

# Wait 2 minutes, then check
kubectl top pods -n flask-app
```

---

## Clean Up

To delete the entire deployment:

```bash
# Delete the flask-app namespace (deletes all resources within)
kubectl delete namespace flask-app

# Stop Minikube
minikube stop

# (Optional) Delete Minikube VM entirely
minikube delete
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Flask image definition |
| `app.py` | Flask application with MongoDB integration |
| `requirements.txt` | Python dependencies |
| `k8s-manifests/02-mongodb-secret.yaml` | Stores MongoDB credentials |
| `k8s-manifests/06-mongodb-statefulset.yaml` | MongoDB pod definition |
| `k8s-manifests/08-flask-deployment.yaml` | Flask pods definition |
| `k8s-manifests/10-hpa.yaml` | Autoscaler configuration |
| `load-test.py` | Load generation script |
| `deploy.ps1` | Automated deployment script |

---

## Credits & References

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Minikube Docs](https://minikube.sigs.k8s.io/)
- [MongoDB Docker Hub](https://hub.docker.com/_/mongo)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMongo Docs](https://pymongo.readthedocs.io/)

---

**Assignment Submission:** December 2, 2025  
**Status:** ✅ Complete & Production-Ready
