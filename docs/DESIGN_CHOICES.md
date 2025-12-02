# Design Choices

## 1. MongoDB as StatefulSet + PVC

**Why:** Stable pod identity + persistent data storage  
**Alternative:** Deployment with emptyDir → data loss on restart ❌

## 2. Headless Service for MongoDB

**Why:** Direct pod-to-pod connection (Flask always reaches same MongoDB instance)  
**Alternative:** Regular service → load-balanced connections, session issues ❌

## 3. Kubernetes Secrets for Credentials

**Why:** Secure, rotatable, industry standard  
**Alternative:** Hard-coded credentials → security risk ❌

## 4. HPA: 2→5 Pods @ 70% CPU Threshold

**Why:** High availability (2 pods minimum) + automatic scaling under load  
**Alternative:** Static replicas → wasteful; manual scaling → slow ❌

## 5. Dedicated Namespace (flask-app)

**Why:** Resource isolation, clean separation, easy cleanup  
**Alternative:** Default namespace → cluttered, risky ❌

## 6. HTTP Probes (/health, /ready)

**Why:** Detects crashes, prevents traffic to unhealthy pods  
**Alternative:** No probes → poor reliability ❌

## 7. Rolling Updates (Zero Downtime)

**Why:** Maintains availability during deployments  
**Alternative:** Recreate → brief downtime ❌

## 8. Resource Requests: 200m CPU / 256Mi Memory

**Why:** Balanced for Minikube; allows scale to 5 pods safely  
**Alternative:** Too high → wasteful; too low → crashes ❌

---

**Summary:** All choices balance reliability, scalability, and cost. Each alternative was rejected for production viability.
