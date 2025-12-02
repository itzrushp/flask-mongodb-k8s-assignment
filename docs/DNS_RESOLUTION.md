# DNS Resolution in Kubernetes

## How It Works

Every Service in Kubernetes gets an automatic DNS entry:
```
<service-name>.<namespace>.svc.cluster.local
```

## Flask Service (Regular)
- DNS: `flask-service.flask-app.svc.cluster.local`
- Resolves to: Service IP (10.104.83.141)
- Purpose: Load-balanced across Flask pods
- Why: Clients don't care which pod responds

## MongoDB Service (Headless)
- DNS: `mongodb-service.flask-app.svc.cluster.local`
- Resolves to: Direct pod IP (10.244.0.4)
- Purpose: Flask always connects to **same** MongoDB instance
- Why: Database needs stable, consistent connections

## Why Headless for MongoDB?

| Aspect | Regular Service | Headless Service |
|--------|-----------------|-----------------|
| **DNS Returns** | Service IP | Pod IP |
| **Load Balancing** | Yes (round-robin) | No (direct) |
| **Use Case** | Stateless services | Stateful services |
| **MongoDB** | Would break | ✅ Correct |

---

## Quick Test

From inside a Flask pod:
```bash
# Resolve Flask service (load-balanced)
nslookup flask-service
# Returns: 10.104.83.141

# Resolve MongoDB service (direct pod)
nslookup mongodb-service
# Returns: 10.244.0.4
```

---

**Key Takeaway:** Headless services enable direct pod-to-pod connections, essential for stateful databases.
