# Exercise 06: Ingress and Load Balancing

## Exercise Overview

**Objective**: Master Kubernetes Ingress controllers for external access, implement load balancing strategies, configure SSL/TLS termination, and set up routing for ML inference services.

**Difficulty**: Intermediate to Advanced
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01-05 (Kubernetes fundamentals)
- Module 005 (Docker networking)

## Learning Objectives

By completing this exercise, you will:
- Install and configure Ingress controllers (Nginx, Traefik)
- Implement path-based and host-based routing rules
- Configure SSL/TLS termination with certificates
- Design load balancing strategies for high-traffic applications
- Enable sticky sessions for stateful applications
- Apply rate limiting to protect backend services
- Build ML inference routing patterns for A/B testing
- Deploy production-grade ingress configurations
- Troubleshoot common ingress and routing issues
- Optimize ingress performance for ML workloads

---

## Part 1: Ingress Basics

### Step 1.1: Install Ingress Controller

```bash
# Install Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx

# Get external IP (LoadBalancer) or NodePort
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### Step 1.2: Simple Ingress Resource

```yaml
# Create backend application
cat > backend-app.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:
      - name: hello
        image: hashicorp/http-echo
        args:
        - "-text=Hello from Kubernetes!"
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: hello-service
spec:
  selector:
    app: hello
  ports:
  - port: 80
    targetPort: 5678
EOF

kubectl apply -f backend-app.yaml

# Create Ingress
cat > ingress-basic.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hello-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /hello
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF

kubectl apply -f ingress-basic.yaml

# Check ingress
kubectl get ingress
kubectl describe ingress hello-ingress

# Test (replace with actual ingress IP)
INGRESS_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$INGRESS_IP/hello
```

### Step 1.3: Host-Based Routing

```yaml
cat > ingress-host-based.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
      version: v1
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      containers:
      - name: app
        image: hashicorp/http-echo
        args: ["-text=Version 1"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-v2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
      version: v2
  template:
    metadata:
      labels:
        app: myapp
        version: v2
    spec:
      containers:
      - name: app
        image: hashicorp/http-echo
        args: ["-text=Version 2"]
---
apiVersion: v1
kind: Service
metadata:
  name: app-v1-service
spec:
  selector:
    app: myapp
    version: v1
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: app-v2-service
spec:
  selector:
    app: myapp
    version: v2
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-based-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: v1.myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-v1-service
            port:
              number: 80
  - host: v2.myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-v2-service
            port:
              number: 80
EOF

kubectl apply -f ingress-host-based.yaml

# Test with host headers
curl -H "Host: v1.myapp.com" http://$INGRESS_IP/
curl -H "Host: v2.myapp.com" http://$INGRESS_IP/
```

✅ **Checkpoint**: You can create basic Ingress resources.

---

## Part 2: SSL/TLS Termination

### Step 2.1: Create TLS Certificate

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=myapp.example.com/O=myapp"

# Create TLS secret
kubectl create secret tls tls-secret \
  --cert=tls.crt \
  --key=tls.key

# Verify secret
kubectl get secret tls-secret

# Cleanup local files
rm tls.key tls.crt
```

### Step 2.2: HTTPS Ingress

```yaml
cat > ingress-tls.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  annotations:
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: tls-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF

kubectl apply -f ingress-tls.yaml

# Test HTTPS (use -k to skip cert verification for self-signed)
curl -k -H "Host: myapp.example.com" https://$INGRESS_IP/
```

### Step 2.3: Let's Encrypt with Cert-Manager

```bash
# Install cert-manager (certificate automation)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager
kubectl wait --for=condition=ready pod -l app=cert-manager -n cert-manager --timeout=120s

# Create ClusterIssuer for Let's Encrypt
cat > letsencrypt-issuer.yaml << 'EOF'
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com  # Change this!
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

kubectl apply -f letsencrypt-issuer.yaml

# Ingress with automatic certificate
cat > ingress-auto-tls.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: auto-tls-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls  # Created automatically
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF

kubectl apply -f ingress-auto-tls.yaml

# Check certificate
kubectl get certificate
kubectl describe certificate myapp-tls
```

✅ **Checkpoint**: You can configure SSL/TLS termination.

---

## Part 3: Advanced Routing

### Step 3.1: Path-Based Routing

```yaml
cat > multi-service-ingress.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: hashicorp/http-echo
        args: ["-text=API Service"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: hashicorp/http-echo
        args: ["-text=Web Service"]
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-based-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /api(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /web(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
EOF

kubectl apply -f multi-service-ingress.yaml

# Test different paths
curl http://$INGRESS_IP/api
curl http://$INGRESS_IP/web
curl http://$INGRESS_IP/
```

### Step 3.2: Canary Deployments with Ingress

```yaml
cat > canary-ingress.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      version: stable
  template:
    metadata:
      labels:
        app: myapp
        version: stable
    spec:
      containers:
      - name: app
        image: hashicorp/http-echo
        args: ["-text=Stable Version"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      version: canary
  template:
    metadata:
      labels:
        app: myapp
        version: canary
    spec:
      containers:
      - name: app
        image: hashicorp/http-echo
        args: ["-text=Canary Version"]
---
apiVersion: v1
kind: Service
metadata:
  name: app-stable-service
spec:
  selector:
    app: myapp
    version: stable
  ports:
  - port: 80
    targetPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: app-canary-service
spec:
  selector:
    app: myapp
    version: canary
  ports:
  - port: 80
    targetPort: 5678
---
# Main ingress (stable)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-stable-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-stable-service
            port:
              number: 80
---
# Canary ingress (10% traffic)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-canary-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-canary-service
            port:
              number: 80
EOF

kubectl apply -f canary-ingress.yaml

# Test multiple times - ~10% should hit canary
for i in {1..20}; do
  curl -H "Host: myapp.com" http://$INGRESS_IP/
done
```

### Step 3.3: Header-Based Routing

```yaml
cat > header-routing.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: header-canary-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-by-header: "X-Canary"
    nginx.ingress.kubernetes.io/canary-by-header-value: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-canary-service
            port:
              number: 80
EOF

kubectl apply -f header-routing.yaml

# Test with header
curl -H "Host: myapp.com" -H "X-Canary: true" http://$INGRESS_IP/
# Gets canary version

curl -H "Host: myapp.com" http://$INGRESS_IP/
# Gets stable version
```

✅ **Checkpoint**: You can implement advanced routing patterns.

---

## Part 4: Load Balancing Strategies

### Step 4.1: Session Affinity (Sticky Sessions)

```yaml
cat > sticky-sessions.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sticky-ingress
  annotations:
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "route"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
    nginx.ingress.kubernetes.io/session-cookie-samesite: "Lax"
spec:
  ingressClassName: nginx
  rules:
  - host: sticky.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-stable-service
            port:
              number: 80
EOF

kubectl apply -f sticky-sessions.yaml

# Test - requests go to same pod
curl -c cookies.txt -b cookies.txt -H "Host: sticky.example.com" http://$INGRESS_IP/
# Subsequent requests use same backend
```

### Step 4.2: Load Balancing Algorithms

```yaml
cat > load-balancing-config.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: lb-ingress
  annotations:
    # Round-robin (default)
    nginx.ingress.kubernetes.io/load-balance: "round_robin"

    # Least connections
    # nginx.ingress.kubernetes.io/load-balance: "least_conn"

    # IP hash
    # nginx.ingress.kubernetes.io/load-balance: "ip_hash"

    # Custom upstream config
    nginx.ingress.kubernetes.io/upstream-vhost: "myapp.local"
spec:
  ingressClassName: nginx
  rules:
  - host: lb.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-stable-service
            port:
              number: 80
EOF
```

### Step 4.3: Connection Pooling and Timeouts

```yaml
cat > timeouts-ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: timeout-ingress
  annotations:
    # Timeout settings
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"

    # Buffer settings
    nginx.ingress.kubernetes.io/proxy-buffer-size: "8k"
    nginx.ingress.kubernetes.io/proxy-buffers-number: "4"

    # Keep-alive
    nginx.ingress.kubernetes.io/upstream-keepalive-connections: "100"
    nginx.ingress.kubernetes.io/upstream-keepalive-timeout: "60"

    # Max body size (important for file uploads)
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
spec:
  ingressClassName: nginx
  rules:
  - host: timeout.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF

kubectl apply -f timeouts-ingress.yaml
```

✅ **Checkpoint**: You understand load balancing strategies.

---

## Part 5: Rate Limiting and Security

### Step 5.1: Rate Limiting

```yaml
cat > rate-limit-ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rate-limited-ingress
  annotations:
    # Rate limit: 10 requests per second per IP
    nginx.ingress.kubernetes.io/limit-rps: "10"

    # Rate limit: 100 connections per IP
    nginx.ingress.kubernetes.io/limit-connections: "100"

    # Whitelist specific IPs
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8,172.16.0.0/12"
spec:
  ingressClassName: nginx
  rules:
  - host: ratelimit.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF

kubectl apply -f rate-limit-ingress.yaml

# Test rate limiting
for i in {1..20}; do
  curl -H "Host: ratelimit.example.com" http://$INGRESS_IP/ &
done
# Some requests should get 503 (rate limited)
```

### Step 5.2: Authentication

```yaml
cat > basic-auth-ingress.yaml << 'EOF'
# Create basic auth credentials
# htpasswd -c auth username
# kubectl create secret generic basic-auth --from-file=auth
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: auth-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-realm: 'Authentication Required'
spec:
  ingressClassName: nginx
  rules:
  - host: auth.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF

# Create auth file
kubectl create secret generic basic-auth \
  --from-literal=auth="$(echo -n 'admin:' && openssl passwd -stdin <<< 'password')"

kubectl apply -f basic-auth-ingress.yaml

# Test with credentials
curl -u admin:password -H "Host: auth.example.com" http://$INGRESS_IP/
```

### Step 5.3: CORS Configuration

```yaml
cat > cors-ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cors-ingress
  annotations:
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://example.com"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization"
    nginx.ingress.kubernetes.io/cors-max-age: "86400"
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
EOF

kubectl apply -f cors-ingress.yaml
```

✅ **Checkpoint**: You can implement security features in Ingress.

---

## Part 6: ML Inference Routing

### Step 6.1: Model Version Routing

```yaml
cat > ml-model-routing.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
      version: v1
  template:
    metadata:
      labels:
        app: ml-inference
        version: v1
    spec:
      containers:
      - name: inference
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        # Your model serving code here
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-v2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
      version: v2
  template:
    metadata:
      labels:
        app: ml-inference
        version: v2
    spec:
      containers:
      - name: inference
        image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
        # Your model serving code here
---
apiVersion: v1
kind: Service
metadata:
  name: model-v1-service
spec:
  selector:
    app: ml-inference
    version: v1
  ports:
  - port: 8000
    targetPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: model-v2-service
spec:
  selector:
    app: ml-inference
    version: v2
  ports:
  - port: 8000
    targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-inference-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"  # Large inputs
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"  # 5 min for inference
spec:
  ingressClassName: nginx
  rules:
  - host: ml.example.com
    http:
      paths:
      - path: /v1/predict
        pathType: Prefix
        backend:
          service:
            name: model-v1-service
            port:
              number: 8000
      - path: /v2/predict
        pathType: Prefix
        backend:
          service:
            name: model-v2-service
            port:
              number: 8000
EOF

kubectl apply -f ml-model-routing.yaml
```

### Step 6.2: A/B Testing for ML Models

```yaml
cat > ml-ab-testing.yaml << 'EOF'
# Stable model (90% traffic)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-stable-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: ml.example.com
    http:
      paths:
      - path: /predict
        pathType: Prefix
        backend:
          service:
            name: model-v1-service
            port:
              number: 8000
---
# Experimental model (10% traffic)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-canary-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
spec:
  ingressClassName: nginx
  rules:
  - host: ml.example.com
    http:
      paths:
      - path: /predict
        pathType: Prefix
        backend:
          service:
            name: model-v2-service
            port:
              number: 8000
EOF

kubectl apply -f ml-ab-testing.yaml

# Monitor both versions
# Gradually increase canary-weight from 10 → 25 → 50 → 100
```

### Step 6.3: Request-Based Routing for ML

```yaml
cat > ml-request-routing.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-cpu-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: ml.example.com
    http:
      paths:
      - path: /predict/cpu
        pathType: Prefix
        backend:
          service:
            name: model-cpu-service
            port:
              number: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-gpu-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"  # 10 min for GPU
spec:
  ingressClassName: nginx
  rules:
  - host: ml.example.com
    http:
      paths:
      - path: /predict/gpu
        pathType: Prefix
        backend:
          service:
            name: model-gpu-service
            port:
              number: 8000
EOF
```

✅ **Checkpoint**: You can route ML inference traffic.

---

## Part 7: Monitoring and Observability

### Step 7.1: Ingress Metrics

```bash
# Nginx Ingress exports Prometheus metrics
kubectl get svc -n ingress-nginx

# Access metrics endpoint
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller-metrics 10254:10254

# In another terminal
curl http://localhost:10254/metrics | grep nginx_
```

### Step 7.2: Access Logging

```yaml
cat > logging-ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: logging-ingress
  annotations:
    # Custom log format
    nginx.ingress.kubernetes.io/configuration-snippet: |
      access_log /var/log/nginx/access.log main;
      error_log /var/log/nginx/error.log;
spec:
  ingressClassName: nginx
  rules:
  - host: logging.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF

# View ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller -f
```

### Step 7.3: Request Tracing

```yaml
cat > tracing-ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tracing-ingress
  annotations:
    # Enable request tracing
    nginx.ingress.kubernetes.io/enable-opentracing: "true"

    # Add request ID
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header X-Request-ID $request_id;
spec:
  ingressClassName: nginx
  rules:
  - host: tracing.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-service
            port:
              number: 80
EOF
```

✅ **Checkpoint**: You can monitor Ingress traffic.

---

## Part 8: Production Best Practices

### Step 8.1: Complete Production Ingress

```yaml
cat > production-ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: production-ingress
  annotations:
    # TLS
    cert-manager.io/cluster-issuer: letsencrypt-prod

    # Security
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.2 TLSv1.3"

    # Rate limiting
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/limit-connections: "1000"

    # Timeouts
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"

    # Size limits
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"

    # CORS
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://example.com"

    # Security headers
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header X-Frame-Options "SAMEORIGIN";
      add_header X-Content-Type-Options "nosniff";
      add_header X-XSS-Protection "1; mode=block";
      add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Connection pooling
    nginx.ingress.kubernetes.io/upstream-keepalive-connections: "100"

    # Load balancing
    nginx.ingress.kubernetes.io/load-balance: "least_conn"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
EOF
```

### Step 8.2: High Availability Setup

```bash
# Scale ingress controller
kubectl scale deployment ingress-nginx-controller \
  -n ingress-nginx --replicas=3

# Use PodDisruptionBudget
cat > ingress-pdb.yaml << 'EOF'
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
EOF

kubectl apply -f ingress-pdb.yaml
```

✅ **Checkpoint**: You can deploy production-ready Ingress.

---

## Summary

**What You Accomplished**:
✅ Installed and configured Ingress controllers
✅ Implemented path and host-based routing
✅ Configured SSL/TLS termination
✅ Implemented canary deployments
✅ Applied load balancing strategies
✅ Configured rate limiting and security
✅ Routed ML inference traffic
✅ Monitored Ingress performance
✅ Applied production best practices

**Key Concepts**:
- Ingress provides HTTP(S) routing
- Multiple routing strategies (path, host, header)
- SSL/TLS automation with cert-manager
- Canary and A/B testing
- Rate limiting and security
- Session affinity for stateful apps
- ML-specific routing patterns

**Production Patterns**:
- Always use TLS in production
- Implement rate limiting
- Use cert-manager for certificate automation
- Monitor ingress metrics
- Scale ingress controllers for HA
- Use PodDisruptionBudgets

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate to Advanced
