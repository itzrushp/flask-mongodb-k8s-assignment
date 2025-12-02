# Troubleshooting Guide

## Pod Issues

### Pod Stuck in Pending
```bash
kubectl describe pod <pod-name> -n flask-app

# Solutions:
minikube start --cpus=4 --memory=8g  # Increase resources
kubectl get pvc -n flask-app          # Check PVC bound
docker push rcoem2022/flask-mongodb-app:latest  # Push image
```

### Pod in CrashLoopBackOff
```bash
kubectl logs <pod-name> -n flask-app  # Check errors

# Common fixes:
kubectl apply -f Dockerfile           # Rebuild image
kubectl rollout restart deployment flask-app -n flask-app
```

### ImagePullBackOff
```bash
docker build -t rcoem2022/flask-mongodb-app:latest .
docker push rcoem2022/flask-mongodb-app:latest
kubectl rollout restart deployment flask-app -n flask-app
```

---

## Connectivity Issues

### Service Unreachable
```bash
# Terminal A (keep open):
minikube service flask-service -n flask-app

# Terminal B:
curl http://127.0.0.1:<port>/
```

### MongoDB Connection Failed
```bash
# Check MongoDB is running:
kubectl get pod mongodb-0 -n flask-app

# Check connectivity:
kubectl exec -it <flask-pod> -n flask-app -- nc -zv mongodb-service 27017

# Verify credentials:
kubectl get secret mongodb-secret -n flask-app -o yaml
```

---

## HPA Issues

### Metrics Showing Unknown
```bash
minikube addons enable metrics-server
sleep 120  # Wait 2 minutes
kubectl get hpa -n flask-app
```

### Not Scaling During Load
```bash
# Check resource requests defined:
kubectl get deployment flask-app -n flask-app -o yaml | grep -A 5 "requests:"

# Generate load:
python load-test.py
```

---

## Quick Reset
```bash
kubectl delete namespace flask-app
minikube stop
minikube start --cpus=4 --memory=6g
minikube addons enable metrics-server
./deploy.ps1
```

---

## Verification Checklist
- ✅ All pods showing `1/1 Running`: `kubectl get pods -n flask-app`
- ✅ Can access app: `curl http://127.0.0.1:<port>/`
- ✅ Database working: `curl -X POST http://127.0.0.1:<port>/data -d '{"test":"data"}'`
- ✅ HPA showing metrics: `kubectl get hpa -n flask-app`
- ✅ Load test works: `python load-test.py`
- ✅ Pods scale during load: Watch replicas increase to 4+
