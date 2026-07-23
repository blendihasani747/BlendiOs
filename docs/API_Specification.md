# BlendiOS — FastAPI REST API Specification

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** OAuth2 Password Bearer (`Authorization: Bearer <token>`)

---

## 1. Authentication

### 1.1 Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request (form data):**

| Field | Type | Required |
|---|---|---|
| `username` | string | yes |
| `password` | string | yes |

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

---

### 1.2 Refresh Token

```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### 1.3 Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### 1.4 Register User (Admin only)

```http
POST /api/v1/auth/register
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "SecureP@ss123",
  "role": "user"
}
```

**Response:**

```json
{
  "id": 3,
  "username": "newuser",
  "role": "user",
  "created_at": "2026-07-02T10:00:00Z"
}
```

---

## 2. Users

### 2.1 List Users

```http
GET /api/v1/users
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "total": 2,
  "items": [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "is_active": true,
      "last_login_at": "2026-07-02T09:00:00Z"
    },
    {
      "id": 2,
      "username": "guest",
      "role": "guest",
      "is_active": true
    }
  ]
}
```

---

### 2.2 Get Current User

```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

---

### 2.3 Get User by ID

```http
GET /api/v1/users/{id}
Authorization: Bearer <access_token>
```

---

### 2.4 Update User

```http
PUT /api/v1/users/{id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "full_name": "Updated Name",
  "role": "user",
  "is_active": true
}
```

---

### 2.5 Delete User

```http
DELETE /api/v1/users/{id}
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

## 3. Files

### 3.1 List Directory

```http
GET /api/v1/files?path=/users/admin/home/Documents
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "path": "/users/admin/home/Documents",
  "items": [
    {
      "name": "report.txt",
      "type": "file",
      "size_bytes": 1024,
      "permissions": "644",
      "updated_at": "2026-07-01T12:00:00Z"
    },
    {
      "name": "Projects",
      "type": "folder",
      "permissions": "755",
      "updated_at": "2026-07-01T10:00:00Z"
    }
  ]
}
```

---

### 3.2 Create File

```http
POST /api/v1/files
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "path": "/users/admin/home/Documents/note.txt",
  "content": "Hello, BlendiOS!",
  "permissions": "644"
}
```

---

### 3.3 Read File

```http
GET /api/v1/files/{path}
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "name": "note.txt",
  "path": "/users/admin/home/Documents/note.txt",
  "content": "Hello, BlendiOS!",
  "size_bytes": 16,
  "mime_type": "text/plain",
  "permissions": "644",
  "owner_id": 1
}
```

---

### 3.4 Update File

```http
PUT /api/v1/files/{path}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "content": "Updated content",
  "permissions": "644"
}
```

---

### 3.5 Delete File

```http
DELETE /api/v1/files/{path}
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "message": "Moved to trash",
  "trash_id": 7
}
```

---

### 3.6 Search Files

```http
POST /api/v1/files/search
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "query": "report",
  "path": "/users/admin/home",
  "type": "file",
  "limit": 20
}
```

**Response:**

```json
{
  "results": [
    {
      "path": "/users/admin/home/Documents/report.txt",
      "name": "report.txt",
      "type": "file",
      "score": 0.95
    }
  ]
}
```

---

### 3.7 Compress Files

```http
POST /api/v1/files/compress
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "paths": [
    "/users/admin/home/Documents/report.txt",
    "/users/admin/home/Documents/Projects"
  ],
  "archive_name": "/users/admin/home/backups/docs.zip",
  "format": "zip"
}
```

---

### 3.8 Decompress Archive

```http
POST /api/v1/files/decompress
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "archive": "/users/admin/home/backups/docs.zip",
  "destination": "/users/admin/home/Restored",
  "format": "zip"
}
```

---

## 4. Applications

### 4.1 List Installed Apps

```http
GET /api/v1/apps
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "apps": [
    {
      "app_id": "file_explorer",
      "name": "File Explorer",
      "version": "1.0.0",
      "category": "system",
      "icon": "icons/file_explorer.png"
    },
    {
      "app_id": "terminal",
      "name": "Terminal",
      "version": "1.0.0",
      "category": "system"
    }
  ]
}
```

---

### 4.2 Launch App

```http
POST /api/v1/apps/{app_id}/launch
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "pid": 42,
  "app_id": "terminal",
  "status": "running",
  "window_id": "win_42"
}
```

---

### 4.3 Install App (Admin)

```http
POST /api/v1/apps
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "app_id": "calculator",
  "source": "app_store",
  "version": "1.0.0"
}
```

---

### 4.4 Uninstall App (Admin)

```http
DELETE /api/v1/apps/{app_id}
Authorization: Bearer <access_token>
```

---

## 5. Processes

### 5.1 List Processes

```http
GET /api/v1/processes
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "processes": [
    {
      "pid": 1,
      "app_id": "desktop_shell",
      "user_id": 1,
      "status": "running",
      "priority": 1,
      "memory_mb": 128,
      "cpu_percent": 2.5,
      "started_at": "2026-07-02T08:00:00Z"
    },
    {
      "pid": 42,
      "app_id": "terminal",
      "user_id": 1,
      "status": "running",
      "priority": 5,
      "memory_mb": 32,
      "cpu_percent": 0.1,
      "started_at": "2026-07-02T09:15:00Z"
    }
  ]
}
```

---

### 5.2 Get Process

```http
GET /api/v1/processes/{pid}
Authorization: Bearer <access_token>
```

---

### 5.3 Kill Process

```http
POST /api/v1/processes/{pid}/kill
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "pid": 42,
  "status": "terminated"
}
```

---

## 6. Settings

### 6.1 Get Settings

```http
GET /api/v1/settings?category=appearance
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "settings": [
    {
      "key": "theme",
      "value": "dark",
      "value_type": "string",
      "category": "appearance"
    },
    {
      "key": "animations_enabled",
      "value": true,
      "value_type": "bool",
      "category": "appearance"
    }
  ]
}
```

---

### 6.2 Update Settings

```http
PUT /api/v1/settings
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**

```json
{
  "settings": [
    {
      "key": "theme",
      "value": "light"
    }
  ]
}
```

---

## 7. Logs

### 7.1 Query Logs

```http
GET /api/v1/logs?level=ERROR&category=security&limit=50&offset=0
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "total": 3,
  "items": [
    {
      "id": 101,
      "timestamp": "2026-07-02T08:30:00Z",
      "level": "ERROR",
      "category": "security",
      "source": "auth_service",
      "message": "Failed login attempt for user 'admin'",
      "ip_address": "127.0.0.1"
    }
  ]
}
```

---

## 8. System

### 8.1 System Status

```http
GET /api/v1/system/status
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "uptime_seconds": 3600,
  "cpu_percent": 12.5,
  "memory": {
    "total_mb": 4096,
    "used_mb": 2048,
    "free_mb": 2048,
    "percent": 50.0
  },
  "storage": {
    "total_bytes": 107374182400,
    "used_bytes": 21474836480,
    "free_bytes": 85899345920
  },
  "active_users": 2,
  "running_processes": 15
}
```

---

### 8.2 Shutdown

```http
POST /api/v1/system/shutdown
Authorization: Bearer <access_token>
```

**Response:** `202 Accepted`

---

## 9. Error Responses

All errors follow this schema:

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": {}
  }
}
```

### Common Error Codes

| HTTP Status | Code | Meaning |
|---|---|---|
| 400 | `BAD_REQUEST` | Invalid input or parameters. |
| 401 | `UNAUTHORIZED` | Missing or invalid token. |
| 403 | `FORBIDDEN` | Insufficient permissions. |
| 404 | `NOT_FOUND` | Resource not found. |
| 409 | `CONFLICT` | Resource already exists or state conflict. |
| 422 | `VALIDATION_ERROR` | Pydantic validation failure. |
| 429 | `RATE_LIMITED` | Too many requests. |
| 500 | `INTERNAL_ERROR` | Unexpected server error. |

---

*End of API Specification*
