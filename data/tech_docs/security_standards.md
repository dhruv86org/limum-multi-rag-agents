# Security Standards and Best Practices

## Overview

This document outlines TechCorp's security standards, best practices, and requirements for all engineering teams. Adherence to these standards is mandatory for all production systems.

## Security Principles

### Defense in Depth
Implement multiple layers of security controls:
- Network security (firewalls, VPCs)
- Application security (input validation, authentication)
- Data security (encryption, access controls)
- Infrastructure security (patching, hardening)
- Monitoring and detection

### Principle of Least Privilege
Grant minimum necessary access:
- Users receive only required permissions
- Service accounts scoped to specific resources
- Regular access reviews and revocation
- Time-limited elevated privileges
- Just-in-time access for sensitive operations

### Security by Design
Build security into the development lifecycle:
- Threat modeling during design phase
- Security requirements in user stories
- Secure coding standards enforced
- Security testing in CI/CD pipeline
- Regular security training for engineers

## Authentication and Authorization

### User Authentication

**Requirements:**
- Multi-factor authentication (MFA) mandatory
- Password complexity: 12+ characters, mixed case, numbers, symbols
- Password expiration: 90 days
- Account lockout: 5 failed attempts
- Session timeout: 30 minutes inactivity

**Allowed Authentication Methods:**
- OAuth 2.0 with PKCE
- SAML 2.0 for enterprise SSO
- WebAuthn for passwordless
- Time-based OTP (TOTP)

**Prohibited:**
- Basic authentication over HTTP
- Plain text password transmission
- Hard-coded credentials
- Shared accounts

### API Authentication

**Best Practices:**
```python
# Good: Use API keys with proper headers
headers = {
    'Authorization': f'Bearer {api_key}',
    'X-API-Version': 'v1'
}
response = requests.get('https://api.techcorp.com/users', headers=headers)

# Bad: API key in URL
response = requests.get(f'https://api.techcorp.com/users?api_key={api_key}')
```

**API Key Management:**
- Keys rotated every 90 days
- Separate keys per environment
- Scoped to minimum necessary permissions
- Logged and monitored for abuse
- Immediately revoked if compromised

### Authorization Models

**Role-Based Access Control (RBAC):**
```yaml
roles:
  - name: viewer
    permissions:
      - read:users
      - read:projects
  
  - name: editor
    permissions:
      - read:users
      - read:projects
      - write:projects
  
  - name: admin
    permissions:
      - read:*
      - write:*
      - delete:*
```

**Attribute-Based Access Control (ABAC):**
```python
def can_access_document(user, document):
    # User must be document owner or in same department
    if user.id == document.owner_id:
        return True
    if user.department == document.department and user.role in ['manager', 'admin']:
        return True
    return False
```

## Data Protection

### Data Classification

**Classification Levels:**

1. **Public**: No harm if disclosed
   - Marketing materials
   - Public documentation
   - Published blog posts

2. **Internal**: Limited harm if disclosed
   - Internal processes
   - Non-sensitive business data
   - General employee information

3. **Confidential**: Significant harm if disclosed
   - Customer data
   - Financial information
   - Business strategies
   - Source code

4. **Restricted**: Severe harm if disclosed
   - PII (Personally Identifiable Information)
   - PHI (Protected Health Information)
   - Payment card data
   - Trade secrets

### Encryption Requirements

**Data at Rest:**
- Confidential and Restricted data: AES-256 encryption
- Database encryption enabled
- Encrypted EBS volumes
- S3 bucket encryption
- Encrypted backups

```python
# Example: Encrypting sensitive data
from cryptography.fernet import Fernet

# Generate key (store in secrets manager)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
sensitive_data = "user@example.com"
encrypted = cipher.encrypt(sensitive_data.encode())

# Decrypt
decrypted = cipher.decrypt(encrypted).decode()
```

**Data in Transit:**
- TLS 1.2 minimum (TLS 1.3 preferred)
- Strong cipher suites only
- Certificate pinning for mobile apps
- HSTS headers on all web applications
- No mixed content (HTTP + HTTPS)

**TLS Configuration:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Data Retention

**Retention Policies:**
- User data: Retained while account active + 30 days
- Logs: 90 days (compliance logs: 7 years)
- Backups: 30 days
- Audit trails: 7 years
- Deleted data: Securely wiped within 30 days

**Data Deletion:**
```python
# Secure deletion example
import os

def secure_delete(filepath):
    """Overwrite file before deletion"""
    size = os.path.getsize(filepath)
    with open(filepath, 'wb') as f:
        f.write(os.urandom(size))
    os.remove(filepath)
```

## Secure Coding Practices

### Input Validation

**Always validate and sanitize user input:**

```python
# Good: Parameterized queries prevent SQL injection
cursor.execute(
    "SELECT * FROM users WHERE email = %s",
    (user_email,)
)

# Bad: String concatenation vulnerable to SQL injection
cursor.execute(
    f"SELECT * FROM users WHERE email = '{user_email}'"
)
```

**Input Validation Checklist:**
- Whitelist allowed characters
- Validate data types
- Check length limits
- Sanitize HTML input
- Validate file uploads
- Reject unexpected formats

### Output Encoding

**Prevent XSS attacks:**

```javascript
// Good: Use framework encoding
<div>{{ user.name }}</div>  // Auto-escaped in most frameworks

// Bad: Direct HTML injection
div.innerHTML = user.name;

// Good: Explicit encoding
div.textContent = user.name;
```

**Context-specific encoding:**
- HTML entity encoding for HTML context
- JavaScript encoding for JS context
- URL encoding for URL parameters
- CSS encoding for CSS context

### Error Handling

**Do not expose sensitive information in errors:**

```python
# Good: Generic error message
try:
    connect_to_database()
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    return {"error": "An internal error occurred. Please try again."}

# Bad: Exposing internal details
try:
    connect_to_database()
except Exception as e:
    return {"error": f"Database connection failed: {e}"}
```

### Secure Dependencies

**Dependency Management:**
- Pin exact versions in production
- Regularly update dependencies
- Scan for known vulnerabilities
- Use only trusted sources
- Review licenses for compliance

**Automated Scanning:**
```bash
# npm audit for Node.js
npm audit
npm audit fix

# pip-audit for Python
pip-audit

# OWASP Dependency Check
dependency-check --project myapp --scan ./
```

## Secrets Management

### Never Commit Secrets

**Prohibited:**
```python
# Bad: Hard-coded secrets
API_KEY = "abc123xyz789"
DATABASE_URL = "postgresql://user:password@localhost/db"
```

**Required:**
```python
# Good: Load from environment
import os
API_KEY = os.environ.get('API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
```

### Secret Storage

**Approved Solutions:**
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets
- Environment variables (for non-prod)

**Secret Rotation:**
```python
import boto3
from datetime import datetime, timedelta

def rotate_secret_if_needed(secret_id):
    client = boto3.client('secretsmanager')
    
    # Get secret metadata
    response = client.describe_secret(SecretId=secret_id)
    last_changed = response.get('LastChangedDate')
    
    # Rotate if older than 90 days
    if datetime.now() - last_changed > timedelta(days=90):
        client.rotate_secret(SecretId=secret_id)
```

### Git Secret Scanning

**Pre-commit hooks:**
```bash
# Install git-secrets
brew install git-secrets

# Configure for repository
git secrets --install
git secrets --register-aws
git secrets --add 'API_KEY.*=.*'
git secrets --add 'SECRET.*=.*'
```

## Application Security

### OWASP Top 10 Protections

**A01: Broken Access Control**
```python
# Verify user authorization for resources
@app.route('/api/documents/<doc_id>')
@login_required
def get_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    # Check if user has access
    if not current_user.can_access(document):
        abort(403)
    
    return jsonify(document.to_dict())
```

**A02: Cryptographic Failures**
```python
# Use strong hashing for passwords
from werkzeug.security import generate_password_hash, check_password_hash

# Hash password
hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

# Verify password
is_valid = check_password_hash(hashed, password)
```

**A03: Injection**
```python
# Use ORMs and parameterized queries
users = User.query.filter_by(email=email).all()  # Safe
users = db.session.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})  # Safe
```

**A04: Insecure Design**
- Threat modeling in design phase
- Security requirements documented
- Secure by default configurations
- Defense in depth architecture

**A05: Security Misconfiguration**
```yaml
# Remove default accounts
# Disable directory listing
# Set secure headers
# Keep systems updated
# Use security scanners
```

**A06: Vulnerable Components**
```bash
# Regular dependency scanning
npm audit
snyk test
trivy image myapp:latest
```

**A07: Authentication Failures**
```python
# Implement rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass
```

**A08: Software and Data Integrity**
```bash
# Sign and verify artifacts
# Use SRI for CDN resources
<script src="https://cdn.example.com/lib.js" 
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
        crossorigin="anonymous"></script>
```

**A09: Logging Failures**
```python
import logging

logger = logging.getLogger(__name__)

# Log security events
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    
    if authenticate(email, password):
        logger.info(f"Successful login: {email}")
        return redirect('/dashboard')
    else:
        logger.warning(f"Failed login attempt: {email} from {request.remote_addr}")
        return "Invalid credentials", 401
```

**A10: Server-Side Request Forgery (SSRF)**
```python
# Validate and whitelist URLs
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url):
    parsed = urlparse(url)
    
    # Only allow HTTPS
    if parsed.scheme != 'https':
        return False
    
    # Block internal IPs
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private:
            return False
    except ValueError:
        pass
    
    # Whitelist allowed domains
    allowed_domains = ['api.example.com', 'cdn.example.com']
    if parsed.hostname not in allowed_domains:
        return False
    
    return True
```

### Security Headers

**Required HTTP Headers:**
```python
# Flask example
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response
```

### Content Security Policy (CSP)

**Strict CSP:**
```
Content-Security-Policy:
  default-src 'none';
  script-src 'self' https://cdn.techcorp.com;
  style-src 'self' https://cdn.techcorp.com;
  img-src 'self' https://images.techcorp.com data:;
  font-src 'self' https://fonts.techcorp.com;
  connect-src 'self' https://api.techcorp.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

## Infrastructure Security

### Cloud Security

**AWS Security Best Practices:**
- Enable GuardDuty for threat detection
- Use Security Groups and NACLs
- Enable CloudTrail for audit logs
- S3 buckets: Block public access by default
- Enable VPC Flow Logs
- Use IAM roles, not access keys
- Enable MFA for root account

**S3 Bucket Security:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

### Container Security

**Dockerfile Security:**
```dockerfile
# Use specific versions, not 'latest'
FROM node:18.19-alpine

# Run as non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

# Copy only necessary files
COPY --chown=nodejs:nodejs package*.json ./
RUN npm ci --only=production
COPY --chown=nodejs:nodejs . .

# Drop capabilities
# Set read-only root filesystem
```

**Kubernetes Security:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
```

### Network Security

**Network Segmentation:**
- Public subnet: Load balancers only
- Private subnet: Application servers
- Isolated subnet: Databases
- Management VPC: Admin access only

**Security Groups:**
```hcl
# Terraform example
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Web tier security group"
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "app" {
  name        = "app-sg"
  description = "Application tier security group"
  
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }
}
```

## Monitoring and Incident Response

### Security Monitoring

**What to Monitor:**
- Failed authentication attempts
- Privilege escalation
- Unusual data access patterns
- Configuration changes
- Network anomalies
- Malware detection

**SIEM Integration:**
```python
import logging
import json

# Structured logging for SIEM
security_logger = logging.getLogger('security')

def log_security_event(event_type, user_id, details):
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': request.remote_addr,
        'user_agent': request.user_agent.string,
        'details': details
    }
    security_logger.warning(json.dumps(event))
```

### Incident Response

**Incident Severity Levels:**

**P0 - Critical:**
- Active data breach
- Complete system outage
- Ransomware attack
- Response time: Immediate

**P1 - High:**
- Potential data breach
- Major security vulnerability
- Partial system compromise
- Response time: < 1 hour

**P2 - Medium:**
- Security policy violation
- Minor vulnerability
- Suspicious activity
- Response time: < 4 hours

**P3 - Low:**
- Security configuration issue
- Informational alert
- False positive investigation
- Response time: < 24 hours

**Incident Response Process:**
1. **Detection**: Alert triggered or issue reported
2. **Analysis**: Assess severity and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Post-Incident**: Review and improve

### Security Incident Playbooks

**Suspected Data Breach:**
1. Activate incident response team
2. Isolate affected systems
3. Preserve evidence (logs, snapshots)
4. Assess scope of data exposure
5. Notify legal and compliance
6. Notify affected users (if required)
7. File breach reports (if required)
8. Conduct root cause analysis
9. Implement corrective measures

**Compromised Credentials:**
1. Immediately revoke credentials
2. Force password reset for affected users
3. Review access logs for unauthorized activity
4. Check for lateral movement
5. Rotate all related secrets
6. Enable additional monitoring
7. Notify security team
8. Document incident timeline

## Compliance and Auditing

### Audit Logging

**What to Log:**
- Authentication and authorization events
- Data access and modifications
- Configuration changes
- Administrative actions
- Security policy violations
- Failed access attempts

**Log Format:**
```json
{
  "timestamp": "2024-01-25T10:30:00Z",
  "event_type": "user.login",
  "user_id": "usr_123",
  "email": "john.doe@example.com",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "status": "success",
  "mfa_used": true,
  "session_id": "sess_abc123"
}
```

### Compliance Requirements

**SOC 2 Type II:**
- Access controls documented and enforced
- Data encryption at rest and in transit
- Audit trails for all system access
- Regular security assessments
- Incident response procedures
- Vendor risk management

**GDPR:**
- Data protection by design
- Right to access and deletion
- Data processing agreements
- Breach notification (72 hours)
- Privacy impact assessments
- Data protection officer

**PCI DSS:**
- Cardholder data never stored
- Use PCI-compliant payment processor
- Network segmentation
- Regular security testing
- Access control enforcement

## Security Testing

### Types of Testing

**Static Application Security Testing (SAST):**
```bash
# SonarQube scan
sonar-scanner \
  -Dsonar.projectKey=myapp \
  -Dsonar.sources=. \
  -Dsonar.host.url=https://sonar.techcorp.com

# Semgrep scan
semgrep --config=auto .
```

**Dynamic Application Security Testing (DAST):**
```bash
# OWASP ZAP scan
zap-cli quick-scan --self-contained https://app.techcorp.com

# Burp Suite scan (via API)
burp-scan https://app.techcorp.com
```

**Dependency Scanning:**
```bash
# Snyk
snyk test
snyk monitor

# OWASP Dependency Check
dependency-check --project myapp --scan ./
```

**Infrastructure Scanning:**
```bash
# Trivy for containers
trivy image myapp:latest

# Checkov for IaC
checkov -d ./terraform

# AWS security scanning
prowler aws
```

### Penetration Testing

**Annual Penetration Testing:**
- External network penetration test
- Web application penetration test
- Social engineering assessment
- Physical security assessment (office)

**Bug Bounty Program:**
- Private program on HackerOne
- Scope: Public web applications and APIs
- Rewards: $100 - $10,000 based on severity
- Response SLA: 72 hours

## Security Training

### Developer Security Training

**Required Training:**
- Secure coding practices (annually)
- OWASP Top 10 (annually)
- Data privacy and GDPR (annually)
- Incident response (annually)
- Social engineering awareness (quarterly)

**Recommended Training:**
- Cloud security certification
- Security conference attendance
- Hands-on security labs (TryHackMe, HackTheBox)

### Security Champions Program

**Security Champions:**
- One per engineering team
- Act as security advocates
- First point of contact for security questions
- Attend monthly security training
- Participate in security reviews

## Contact Information

**Security Team:**
- Email: security@techcorp.com
- Slack: #security
- Emergency: security-oncall@techcorp.com

**Report Security Issues:**
- Internal: security@techcorp.com
- External: security-reports@techcorp.com
- Bug Bounty: HackerOne platform

---

*Security Standards v3.0 - Updated January 2025*
*All standards mandatory for production systems*
