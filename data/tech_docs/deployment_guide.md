# Deployment Guide

## Overview

This guide covers deployment procedures, infrastructure setup, CI/CD pipelines, and best practices for deploying TechCorp applications.

## Architecture Overview

### Production Environment

**Infrastructure Stack:**
- **Cloud Provider**: AWS (us-east-1 primary, us-west-2 failover)
- **Kubernetes**: EKS clusters for container orchestration
- **Database**: RDS PostgreSQL with Multi-AZ
- **Cache**: ElastiCache Redis cluster
- **CDN**: CloudFront for static assets
- **Storage**: S3 for object storage
- **Monitoring**: DataDog, CloudWatch

**Environment Tiers:**
1. **Production** (`prod`): Customer-facing
2. **Staging** (`staging`): Pre-production testing
3. **Development** (`dev`): Integration testing
4. **Local** (`local`): Developer workstations

### Network Architecture

```
Internet
   ↓
CloudFront (CDN)
   ↓
Application Load Balancer
   ↓
   ├─→ Web Tier (EKS)
   ├─→ API Tier (EKS)
   └─→ Worker Tier (EKS)
          ↓
   ┌──────┴──────┐
   ↓             ↓
Database      Cache
(RDS)       (ElastiCache)
```

### Security Architecture

- VPC with public and private subnets
- Security groups restricting traffic
- WAF protecting public endpoints
- Secrets Manager for credentials
- IAM roles for service authentication
- Network ACLs for additional layer

## Prerequisites

### Required Access

Before deploying, ensure you have:
- AWS account access with appropriate IAM permissions
- Kubernetes cluster access (kubectl configured)
- Docker Hub or ECR access for container images
- GitHub repository access for source code
- VPN access for production resources

### Required Tools

Install these tools on your deployment machine:

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Configuration Files

Required configuration files in your project:

- `Dockerfile`: Container image definition
- `kubernetes/*.yaml`: Kubernetes manifests
- `.github/workflows/*.yml`: CI/CD pipelines
- `helm/`: Helm charts for deployment
- `.env.production`: Production environment variables

## CI/CD Pipeline

### GitHub Actions Workflow

Our deployment pipeline uses GitHub Actions with the following stages:

**Workflow File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm install
          npm test
          npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t techcorp/app:${{ github.sha }} .
          docker tag techcorp/app:${{ github.sha }} techcorp/app:latest

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push techcorp/app:${{ github.sha }}
          docker push techcorp/app:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure kubectl
        run: |
          echo ${{ secrets.KUBECONFIG }} | base64 -d > kubeconfig
          export KUBECONFIG=./kubeconfig

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/app app=techcorp/app:${{ github.sha }} -n production
          kubectl rollout status deployment/app -n production
```

### Pipeline Stages

**1. Test Stage**
- Unit tests
- Integration tests
- Linting and code quality checks
- Security scanning
- Coverage reporting

**2. Build Stage**
- Build Docker image
- Tag with commit SHA and 'latest'
- Scan image for vulnerabilities
- Push to container registry

**3. Deploy Stage**
- Update Kubernetes deployment
- Rolling update to new version
- Health checks
- Smoke tests
- Rollback if failures detected

### Branch Strategy

**Branch Flow:**
```
feature/* → dev → staging → main → production
```

**Deployment Triggers:**
- `dev` branch → Auto-deploy to dev environment
- `staging` branch → Auto-deploy to staging
- `main` branch → Manual approval → Production deploy
- Tags (`v*`) → Production release

### Approval Gates

Production deployments require approval:
1. PR approved by 2+ reviewers
2. All CI checks passing
3. Staging deployment successful
4. Security scan clean
5. Manual approval from tech lead

## Docker Deployment

### Building Images

**Development Build:**
```bash
docker build -t techcorp/app:dev .
```

**Production Build:**
```bash
docker build -f Dockerfile.prod -t techcorp/app:latest .
docker tag techcorp/app:latest techcorp/app:v1.2.3
```

### Multi-stage Dockerfile

**Example Dockerfile.prod:**
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

ENV NODE_ENV=production
EXPOSE 3000

USER node
CMD ["node", "dist/server.js"]
```

### Image Optimization

**Best Practices:**
- Use Alpine base images
- Multi-stage builds to reduce size
- .dockerignore to exclude unnecessary files
- Layer caching for faster builds
- Scan images with Trivy or Snyk

### Container Registry

**Push to ECR:**
```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag techcorp/app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/techcorp/app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/techcorp/app:latest
```

## Kubernetes Deployment

### Deployment Manifest

**File:** `kubernetes/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: techcorp-app
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: techcorp-app
  template:
    metadata:
      labels:
        app: techcorp-app
        version: v1.2.3
    spec:
      containers:
      - name: app
        image: techcorp/app:v1.2.3
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service and Ingress

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: techcorp-app
  namespace: production
spec:
  selector:
    app: techcorp-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
```

**Ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: techcorp-app
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - app.techcorp.com
    secretName: techcorp-tls
  rules:
  - host: app.techcorp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: techcorp-app
            port:
              number: 80
```

### Deploying to Kubernetes

**Apply manifests:**
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml
```

**Using Helm:**
```bash
helm upgrade --install techcorp-app ./helm/techcorp-app \
  --namespace production \
  --values helm/values-production.yaml \
  --set image.tag=v1.2.3
```

### Rolling Updates

**Update deployment:**
```bash
kubectl set image deployment/techcorp-app app=techcorp/app:v1.2.4 -n production
```

**Monitor rollout:**
```bash
kubectl rollout status deployment/techcorp-app -n production
```

**Rollback if needed:**
```bash
kubectl rollout undo deployment/techcorp-app -n production
kubectl rollout history deployment/techcorp-app -n production
```

## Database Migrations

### Migration Strategy

**Pre-deployment:**
1. Backup production database
2. Test migrations on staging
3. Review migration scripts
4. Plan rollback procedure

**Migration Tools:**
- **Flyway**: Java-based migrations
- **Liquibase**: XML/SQL/YAML migrations
- **Alembic**: Python migrations
- **Knex**: Node.js migrations

### Running Migrations

**Using Kubernetes Job:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-v1-2-3
  namespace: production
spec:
  template:
    spec:
      containers:
      - name: migration
        image: techcorp/app:v1.2.3
        command: ["npm", "run", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
      restartPolicy: OnFailure
```

**Apply migration:**
```bash
kubectl apply -f kubernetes/migration-job.yaml
kubectl wait --for=condition=complete job/db-migration-v1-2-3 -n production --timeout=300s
```

### Migration Best Practices

- Always write reversible migrations
- Test on copy of production data
- Minimize downtime with backwards-compatible changes
- Use database transactions
- Monitor performance impact
- Have rollback plan ready

## Secrets Management

### AWS Secrets Manager

**Store secret:**
```bash
aws secretsmanager create-secret \
  --name prod/techcorp/database-url \
  --secret-string "postgresql://user:pass@host:5432/db"
```

**Retrieve in application:**
```python
import boto3
import json

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='prod/techcorp/database-url')
secret = json.loads(response['SecretString'])
```

### Kubernetes Secrets

**Create from literal:**
```bash
kubectl create secret generic app-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=api-key='abc123' \
  -n production
```

**Create from file:**
```bash
kubectl create secret generic app-secrets \
  --from-env-file=.env.production \
  -n production
```

**External Secrets Operator:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: app-secrets
  data:
  - secretKey: database-url
    remoteRef:
      key: prod/techcorp/database-url
```

## Monitoring and Observability

### Health Checks

**Health endpoint:**
```javascript
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});
```

**Readiness endpoint:**
```javascript
app.get('/ready', async (req, res) => {
  const dbHealthy = await checkDatabase();
  const cacheHealthy = await checkCache();
  
  if (dbHealthy && cacheHealthy) {
    res.status(200).json({ status: 'ready' });
  } else {
    res.status(503).json({ status: 'not ready' });
  }
});
```

### Logging

**Structured logging:**
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.json(),
  defaultMeta: { service: 'techcorp-app' },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

logger.info('User logged in', { userId: 123, ip: '192.168.1.1' });
```

**Log aggregation:**
- Send logs to CloudWatch Logs
- Use Fluentd/Fluent Bit for forwarding
- Query with CloudWatch Insights
- Set up alerts for errors

### Metrics

**Prometheus metrics:**
```javascript
const prometheus = require('prom-client');

const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status']
});

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration.labels(req.method, req.route.path, res.statusCode).observe(duration);
  });
  next();
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(await prometheus.register.metrics());
});
```

### Alerting

**DataDog monitors:**
- High error rate (>1% of requests)
- Slow response time (p95 > 500ms)
- High memory usage (>80%)
- Pod restarts (>3 in 10 minutes)
- Database connection errors

**PagerDuty integration:**
- Critical alerts page on-call engineer
- Non-critical alerts create incidents
- Escalation policies for unacknowledged alerts

## Disaster Recovery

### Backup Strategy

**Database backups:**
- Automated daily snapshots
- Point-in-time recovery (PITR) enabled
- 30-day retention
- Cross-region replication
- Weekly restore testing

**Configuration backups:**
- Kubernetes manifests in Git
- Secrets exported to secure storage
- Infrastructure as Code (Terraform) in Git

### Restore Procedures

**Database restore:**
```bash
# List snapshots
aws rds describe-db-snapshots --db-instance-identifier prod-db

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier prod-db-restored \
  --db-snapshot-identifier prod-db-snapshot-2024-01-25

# Update application connection string
kubectl set env deployment/techcorp-app DATABASE_URL=new-connection-string -n production
```

**Disaster recovery runbook:**
1. Assess impact and scope
2. Activate incident response team
3. Failover to DR region if necessary
4. Restore from backups
5. Validate data integrity
6. Resume normal operations
7. Post-incident review

## Rollback Procedures

### Application Rollback

**Kubernetes rollback:**
```bash
# Rollback to previous version
kubectl rollout undo deployment/techcorp-app -n production

# Rollback to specific revision
kubectl rollout undo deployment/techcorp-app --to-revision=5 -n production

# Verify rollback
kubectl rollout status deployment/techcorp-app -n production
```

### Database Rollback

**Schema rollback:**
```bash
# Run down migration
npm run migrate:rollback

# Or restore from backup
# (See disaster recovery section)
```

### Rollback Decision Tree

Execute rollback if:
- Error rate >5% within 5 minutes of deployment
- Critical functionality broken
- Data corruption detected
- Performance degraded >50%

## Security Best Practices

### Image Security

**Scan images:**
```bash
# Trivy scan
trivy image techcorp/app:v1.2.3

# Snyk scan
snyk container test techcorp/app:v1.2.3
```

**Sign images:**
```bash
# Using Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker push techcorp/app:v1.2.3
```

### Runtime Security

**Pod Security Standards:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
```

**Network Policies:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: techcorp-app
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: techcorp-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Compliance

**SOC 2 requirements:**
- All deployments logged and auditable
- Access controls with least privilege
- Encryption in transit and at rest
- Regular security scanning
- Incident response procedures

## Troubleshooting

### Common Issues

**Pod not starting:**
```bash
# Check pod status
kubectl get pods -n production

# View events
kubectl describe pod techcorp-app-xxx -n production

# Check logs
kubectl logs techcorp-app-xxx -n production

# Check previous container logs
kubectl logs techcorp-app-xxx -n production --previous
```

**Service not accessible:**
```bash
# Check service
kubectl get svc -n production

# Check endpoints
kubectl get endpoints -n production

# Test service internally
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
wget -O- http://techcorp-app.production.svc.cluster.local
```

**High memory usage:**
```bash
# Check resource usage
kubectl top pods -n production

# Get heap dump (Node.js)
kubectl exec techcorp-app-xxx -n production -- npm run heap-dump

# Increase resources
kubectl set resources deployment/techcorp-app --limits=memory=1Gi -n production
```

### Debug Checklist

- [ ] Check pod status and events
- [ ] Review application logs
- [ ] Verify environment variables
- [ ] Confirm secrets are loaded
- [ ] Test network connectivity
- [ ] Check resource limits
- [ ] Review recent changes
- [ ] Query metrics and traces

---

*Deployment Guide v2.0 - Updated January 2025*
