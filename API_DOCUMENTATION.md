# API Documentation

## Overview

This document provides comprehensive API documentation for the ViT Deepfake Detector application.

## Base URL

```
http://localhost:5000/api
```

## Authentication

All protected endpoints require active user session. Use Flask-Login session management.

### Session-based Authentication

```bash
# Create session via login
POST /api/auth/login

# Session automatically managed by Flask-Login
# Logout to destroy session
POST /api/auth/logout
```

## Response Format

All responses are JSON formatted:

```json
{
  "status": "success|error",
  "data": {},
  "message": "Response message"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 500 | Server Error - Internal error |

## Authentication Endpoints

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "username": "string (min 3 chars)",
  "email": "string (valid email)",
  "password": "string (min 8, 1 upper, 1 digit)",
  "confirm_password": "string (must match password)"
}
```

**Response (201)**
```json
{
  "message": "Registration successful",
  "user_id": "uuid",
  "username": "string"
}
```

**Errors**
- 400: Invalid input
- 409: Username or email already exists

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "string (username or email)",
  "password": "string",
  "remember": "boolean (optional)"
}
```

**Response (200)**
```json
{
  "message": "Login successful",
  "user_id": "uuid",
  "username": "string",
  "email": "string"
}
```

**Errors**
- 400: Missing credentials
- 401: Invalid credentials
- 403: Account disabled

### Get Current User

```http
GET /auth/me
```

**Response (200)**
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "created_at": "ISO 8601 timestamp"
}
```

**Errors**
- 401: Not authenticated

### Logout

```http
POST /auth/logout
```

**Response (200)**
```json
{
  "message": "Logout successful"
}
```

### Change Password

```http
POST /auth/change-password
Content-Type: application/json

{
  "old_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**Response (200)**
```json
{
  "message": "Password changed successfully"
}
```

**Errors**
- 400: Invalid password format
- 401: Current password incorrect
- 401: Not authenticated

## Detection Endpoints

### Upload and Detect

```http
POST /detection/upload
Content-Type: multipart/form-data

file: <image file> (JPEG, PNG, BMP, GIF - max 16MB)
```

**Response (200)**
```json
{
  "detection_id": "uuid",
  "prediction": "REAL|DEEPFAKE",
  "confidence": 0.95,
  "processing_time": 1.23,
  "filename": "string",
  "message": "Image classified as..."
}
```

**Errors**
- 400: No file or invalid format
- 401: Not authenticated
- 413: File too large

### Get Detection History

```http
GET /detection/history?page=1&limit=10
```

**Query Parameters**
- `page`: Integer (default: 1)
- `limit`: Integer 1-100 (default: 10)

**Response (200)**
```json
{
  "detections": [
    {
      "id": "uuid",
      "filename": "string",
      "prediction": "REAL|DEEPFAKE",
      "confidence": 0.95,
      "processing_time": 1.23,
      "created_at": "ISO 8601 timestamp"
    }
  ],
  "total": 42,
  "pages": 5,
  "current_page": 1
}
```

**Errors**
- 400: Invalid pagination
- 401: Not authenticated

### Get Detection Details

```http
GET /detection/details/{detection_id}
```

**Response (200)**
```json
{
  "id": "uuid",
  "filename": "string",
  "prediction": "REAL|DEEPFAKE",
  "confidence": 0.95,
  "processing_time": 1.23,
  "created_at": "ISO 8601 timestamp"
}
```

**Errors**
- 404: Detection not found
- 401: Not authenticated

### Delete Detection

```http
DELETE /detection/delete/{detection_id}
```

**Response (200)**
```json
{
  "message": "Detection deleted successfully"
}
```

**Errors**
- 404: Detection not found
- 401: Not authenticated

### Get Statistics

```http
GET /detection/stats
```

**Response (200)**
```json
{
  "total_detections": 42,
  "real_images": 25,
  "deepfake_images": 17,
  "average_confidence": 0.9234
}
```

**Errors**
- 401: Not authenticated

## Example Requests

### Complete Workflow

**1. Register**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","email":"john@example.com","password":"MyPass123","confirm_password":"MyPass123"}' \
  -c cookies.txt
```

**2. Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"MyPass123"}' \
  -c cookies.txt
```

**3. Upload Image**
```bash
curl -X POST http://localhost:5000/api/detection/upload \
  -F "file=@image.jpg" \
  -b cookies.txt
```

**4. Get History**
```bash
curl -X GET "http://localhost:5000/api/detection/history?page=1&limit=20" \
  -b cookies.txt
```

**5. Get Statistics**
```bash
curl -X GET http://localhost:5000/api/detection/stats \
  -b cookies.txt
```

**6. Logout**
```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -b cookies.txt
```

## Rate Limiting

Recommended rate limits:
- Register: 5 requests per hour per IP
- Login: 10 requests per hour per IP
- Upload: 60 requests per hour per user
- History: 100 requests per hour per user

## Pagination

- Maximum `limit`: 100
- Default `limit`: 10
- Pages are 1-indexed

## Date Format

All timestamps use ISO 8601 format:
```
2026-02-21T10:30:45.123456
```

## CORS

CORS is enabled for all origins in development. Configure as needed in production:

```python
CORS(app, origins=['https://yourdomain.com'])
```

## Versioning

Current API version: v1
Future versions may be accessed via `/api/v2/`, etc.

---

For questions or issues, refer to the main README.md
