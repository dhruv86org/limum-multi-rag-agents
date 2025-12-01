# TechCorp API Documentation

## Overview

TechCorp provides a comprehensive RESTful API for integrating with our platform. This documentation covers authentication, endpoints, rate limits, and best practices.

## Base URL

```
Production: https://api.techcorp.com/v1
Staging: https://api-staging.techcorp.com/v1
Sandbox: https://api-sandbox.techcorp.com/v1
```

## Authentication

### API Keys

All API requests require authentication using API keys.

**Obtaining API Keys:**
1. Log into your TechCorp account
2. Navigate to Settings > API Keys
3. Click "Generate New API Key"
4. Store the key securely (shown only once)

**Authentication Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**Example Request:**
```bash
curl -H "Authorization: Bearer tc_live_abc123xyz" \
  https://api.techcorp.com/v1/users
```

### Key Types

**Live Keys** (`tc_live_*`)
- Used in production
- Real data and transactions
- Rate limits apply

**Test Keys** (`tc_test_*`)
- Used for development/testing
- Sandbox environment
- No real charges
- Same functionality as live

### OAuth 2.0

For third-party integrations, use OAuth 2.0:

**Authorization Endpoint:**
```
GET https://auth.techcorp.com/oauth/authorize
  ?client_id={CLIENT_ID}
  &redirect_uri={REDIRECT_URI}
  &response_type=code
  &scope=read_users,write_data
```

**Token Exchange:**
```
POST https://auth.techcorp.com/oauth/token
Content-Type: application/json

{
  "grant_type": "authorization_code",
  "code": "AUTH_CODE",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "redirect_uri": "YOUR_REDIRECT_URI"
}
```

**Scopes:**
- `read_users`: Read user data
- `write_users`: Create/update users
- `read_data`: Read application data
- `write_data`: Create/update application data
- `delete_data`: Delete application data
- `admin`: Full administrative access

## Rate Limiting

### Rate Limit Tiers

**Free Tier:**
- 1,000 requests per hour
- 10,000 requests per day
- 5 requests per second

**Pro Tier:**
- 10,000 requests per hour
- 100,000 requests per day
- 50 requests per second

**Enterprise Tier:**
- Custom limits
- Dedicated infrastructure
- SLA guarantees

### Rate Limit Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640995200
```

### Exceeding Rate Limits

When rate limit exceeded:
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 300 seconds.",
    "retry_after": 300
  }
}
```

HTTP Status: `429 Too Many Requests`

### Best Practices
- Implement exponential backoff
- Cache responses when possible
- Use webhooks instead of polling
- Batch requests when supported

## Users API

### List Users

Retrieve a paginated list of users.

**Endpoint:**
```
GET /users
```

**Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Results per page (default: 20, max: 100)
- `sort` (string): Sort field (default: created_at)
- `order` (string): Sort order - asc, desc (default: desc)
- `status` (string): Filter by status - active, inactive, pending
- `search` (string): Search query

**Example Request:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.techcorp.com/v1/users?page=1&per_page=50&status=active"
```

**Response:**
```json
{
  "data": [
    {
      "id": "usr_abc123",
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "status": "active",
      "role": "admin",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 50,
    "total_pages": 5,
    "total_count": 234
  }
}
```

### Get User

Retrieve a specific user by ID.

**Endpoint:**
```
GET /users/{user_id}
```

**Example Request:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.techcorp.com/v1/users/usr_abc123
```

**Response:**
```json
{
  "id": "usr_abc123",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-555-123-4567",
  "status": "active",
  "role": "admin",
  "department": "Engineering",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z",
  "metadata": {
    "employee_id": "EMP001",
    "location": "San Francisco"
  }
}
```

### Create User

Create a new user.

**Endpoint:**
```
POST /users
```

**Request Body:**
```json
{
  "email": "jane.smith@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1-555-987-6543",
  "role": "member",
  "department": "Marketing",
  "metadata": {
    "employee_id": "EMP002",
    "location": "New York"
  }
}
```

**Response:**
```json
{
  "id": "usr_xyz789",
  "email": "jane.smith@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "status": "pending",
  "created_at": "2024-01-25T09:15:00Z"
}
```

### Update User

Update an existing user.

**Endpoint:**
```
PATCH /users/{user_id}
```

**Request Body:**
```json
{
  "department": "Sales",
  "role": "admin",
  "metadata": {
    "location": "Austin"
  }
}
```

### Delete User

Delete a user (soft delete).

**Endpoint:**
```
DELETE /users/{user_id}
```

**Response:**
```json
{
  "id": "usr_abc123",
  "deleted": true,
  "deleted_at": "2024-01-25T16:30:00Z"
}
```

## Projects API

### List Projects

Retrieve all projects.

**Endpoint:**
```
GET /projects
```

**Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Results per page
- `status` (string): active, completed, archived
- `owner_id` (string): Filter by owner user ID
- `tag` (string): Filter by tag

**Response:**
```json
{
  "data": [
    {
      "id": "proj_abc123",
      "name": "Website Redesign",
      "description": "Complete redesign of corporate website",
      "status": "active",
      "owner_id": "usr_abc123",
      "team_members": ["usr_abc123", "usr_xyz789"],
      "tags": ["design", "website"],
      "start_date": "2024-01-01",
      "end_date": "2024-03-31",
      "created_at": "2023-12-15T10:00:00Z"
    }
  ]
}
```

### Create Project

**Endpoint:**
```
POST /projects
```

**Request Body:**
```json
{
  "name": "Mobile App Development",
  "description": "iOS and Android mobile app",
  "status": "active",
  "owner_id": "usr_abc123",
  "team_members": ["usr_abc123", "usr_xyz789"],
  "tags": ["mobile", "ios", "android"],
  "start_date": "2024-02-01",
  "end_date": "2024-06-30"
}
```

### Update Project

**Endpoint:**
```
PATCH /projects/{project_id}
```

### Delete Project

**Endpoint:**
```
DELETE /projects/{project_id}
```

## Tasks API

### List Tasks

**Endpoint:**
```
GET /tasks
```

**Parameters:**
- `project_id` (string): Filter by project
- `assignee_id` (string): Filter by assignee
- `status` (string): todo, in_progress, done
- `priority` (string): low, medium, high, urgent

**Response:**
```json
{
  "data": [
    {
      "id": "task_abc123",
      "title": "Design homepage mockup",
      "description": "Create high-fidelity mockup for new homepage",
      "status": "in_progress",
      "priority": "high",
      "project_id": "proj_abc123",
      "assignee_id": "usr_xyz789",
      "due_date": "2024-02-15",
      "created_at": "2024-01-20T09:00:00Z"
    }
  ]
}
```

### Create Task

**Endpoint:**
```
POST /tasks
```

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Add OAuth 2.0 authentication",
  "status": "todo",
  "priority": "urgent",
  "project_id": "proj_abc123",
  "assignee_id": "usr_abc123",
  "due_date": "2024-02-20"
}
```

## Webhooks

### Overview

Webhooks allow you to receive real-time notifications about events in your TechCorp account.

### Creating Webhooks

**Endpoint:**
```
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://example.com/webhooks",
  "events": ["user.created", "user.updated", "project.created"],
  "secret": "your_webhook_secret"
}
```

### Webhook Events

Available events:
- `user.created`: New user created
- `user.updated`: User updated
- `user.deleted`: User deleted
- `project.created`: New project created
- `project.updated`: Project updated
- `project.completed`: Project marked complete
- `task.created`: New task created
- `task.updated`: Task updated
- `task.completed`: Task marked complete

### Webhook Payload

**Example Payload:**
```json
{
  "event": "user.created",
  "timestamp": "2024-01-25T10:30:00Z",
  "data": {
    "id": "usr_abc123",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Webhook Signature Verification

Verify webhook authenticity using HMAC:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

The signature is sent in the `X-TechCorp-Signature` header.

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request parameters",
    "details": {
      "email": ["Email is required", "Email must be valid"]
    }
  }
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `204 No Content`: Successful request with no content
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (duplicate)
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Common Error Codes

- `invalid_request`: Malformed request
- `authentication_failed`: Invalid credentials
- `permission_denied`: Insufficient permissions
- `resource_not_found`: Resource doesn't exist
- `validation_error`: Input validation failed
- `rate_limit_exceeded`: Too many requests
- `duplicate_resource`: Resource already exists

## Pagination

All list endpoints support pagination.

**Parameters:**
- `page`: Page number (1-based)
- `per_page`: Items per page (max 100)

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "current_page": 2,
    "per_page": 20,
    "total_pages": 10,
    "total_count": 195,
    "has_next": true,
    "has_prev": true
  }
}
```

**Link Header:**
```
Link: <https://api.techcorp.com/v1/users?page=1>; rel="first",
      <https://api.techcorp.com/v1/users?page=1>; rel="prev",
      <https://api.techcorp.com/v1/users?page=3>; rel="next",
      <https://api.techcorp.com/v1/users?page=10>; rel="last"
```

## Filtering and Sorting

### Filtering

Use query parameters to filter results:

```
GET /users?status=active&role=admin&department=Engineering
```

### Advanced Filtering

Some endpoints support advanced filtering:

```
GET /users?filter[status]=active&filter[created_at][gte]=2024-01-01
```

Operators:
- `eq`: Equals
- `ne`: Not equals
- `gt`: Greater than
- `gte`: Greater than or equal
- `lt`: Less than
- `lte`: Less than or equal
- `in`: In array
- `contains`: Contains substring

### Sorting

```
GET /users?sort=created_at&order=desc
```

Multiple fields:
```
GET /users?sort=department,last_name&order=asc,asc
```

## Idempotency

Safely retry requests using idempotency keys.

**Header:**
```
Idempotency-Key: unique-key-123
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Idempotency-Key: $(uuidgen)" \
     -X POST \
     -d '{"email":"user@example.com"}' \
     https://api.techcorp.com/v1/users
```

Duplicate requests with the same key return the original response.

## Versioning

API version specified in URL:
```
https://api.techcorp.com/v1/users
```

**Current Version:** v1

**Version Support:**
- Current version: Supported indefinitely
- Previous version: Supported for 12 months after deprecation
- Deprecated versions: 6 month notice before shutdown

**Version Header (Optional):**
```
Accept: application/vnd.techcorp.v1+json
```

## SDK and Libraries

### Official SDKs

**Python:**
```python
pip install techcorp-python

from techcorp import TechCorp

client = TechCorp(api_key="YOUR_API_KEY")
users = client.users.list(status="active")
```

**JavaScript/Node.js:**
```javascript
npm install techcorp-node

const TechCorp = require('techcorp-node');
const client = new TechCorp('YOUR_API_KEY');

const users = await client.users.list({ status: 'active' });
```

**Ruby:**
```ruby
gem install techcorp-ruby

require 'techcorp'
client = TechCorp::Client.new(api_key: 'YOUR_API_KEY')
users = client.users.list(status: 'active')
```

## Testing

### Sandbox Environment

Use test API keys in sandbox:
```
https://api-sandbox.techcorp.com/v1
```

**Test Data:**
- Pre-populated with sample data
- No side effects or real charges
- Reset weekly

### Test Cards

For payment testing:
- Success: `4242424242424242`
- Decline: `4000000000000002`
- Error: `4000000000000069`

## Security Best Practices

### API Key Security
- Never commit keys to version control
- Use environment variables
- Rotate keys periodically
- Use different keys for dev/staging/production
- Revoke compromised keys immediately

### HTTPS Only
- All API requests must use HTTPS
- HTTP requests are rejected

### IP Whitelisting
Enterprise plans can whitelist IPs:
1. Navigate to Settings > Security
2. Add allowed IP addresses
3. Save configuration

### Audit Logs
View API activity:
- Settings > Audit Logs
- Filter by user, action, date
- Export for compliance

## Support and Resources

### Documentation
- Full API Reference: https://docs.techcorp.com/api
- Getting Started Guide: https://docs.techcorp.com/quickstart
- Code Examples: https://github.com/techcorp/examples

### Support Channels
- Email: api-support@techcorp.com
- Discord: https://discord.gg/techcorp
- Stack Overflow: Tag `techcorp-api`

### Status Page
Monitor API status: https://status.techcorp.com

### Changelog
API updates: https://docs.techcorp.com/changelog

### Rate Limit Increase
Request higher limits:
- Contact sales@techcorp.com
- Provide use case details
- Enterprise plans include custom limits

---

*API Documentation v1.0 - Updated January 2025*
