# Secure User Authentication System

A comprehensive and secure user authentication system built with FastAPI, SQLAlchemy, and JWT tokens featuring advanced security measures, rate limiting, and role-based access control.

## 🛡️ Security Features

- **JWT Authentication**: Access tokens (30min) + Refresh tokens (7 days)
- **Password Security**: bcrypt hashing with strength validation
- **Rate Limiting**: Configurable limits on sensitive endpoints
- **Input Sanitization**: XSS prevention and input validation
- **CORS Protection**: Configurable cross-origin policies
- **Security Headers**: HSTS, CSP, XSS Protection, etc.
- **Token Blacklisting**: Secure logout with token invalidation
- **Password Reset**: Secure token-based password recovery
- **Account Status**: User activation/deactivation support

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`

### 3. Access Documentation

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## 📋 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Rate Limit | Access |
|--------|----------|-------------|------------|---------|
| `POST` | `/auth/register` | Register a new user | 3/min | Public |
| `POST` | `/auth/login` | Login and get JWT tokens | 5/min | Public |
| `POST` | `/auth/refresh` | Refresh access token | 5/min | Public |
| `POST` | `/auth/logout` | Logout (blacklist token) | 100/min | Public |
| `POST` | `/auth/forgot-password` | Request password reset | 1/min | Public |
| `POST` | `/auth/reset-password` | Reset password with token | 1/min | Public |
| `GET` | `/auth/me` | Get current user info | 100/min | Authenticated |

### Admin-Only Endpoints

| Method | Endpoint | Description | Rate Limit | Access |
|--------|----------|-------------|------------|---------|
| `GET` | `/users` | Get all users | 100/min | Admin |
| `PUT` | `/users/{user_id}/role` | Change user role | 100/min | Admin |
| `DELETE` | `/users/{user_id}` | Delete user | 100/min | Admin |

### System Endpoints

| Method | Endpoint | Description | Rate Limit | Access |
|--------|----------|-------------|------------|---------|
| `GET` | `/health` | Health check | 100/min | Public |

## 🔒 Rate Limiting Rules

- **Login attempts**: 5 per minute per IP
- **Registration**: 3 per minute per IP
- **Password reset**: 1 per minute per IP
- **General API**: 100 per minute per IP

## 🧪 Testing the API

### 1. Health Check

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### 2. Register a User

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 special character (`!@#$%^&*(),.?":{}|<>`)

### 3. Login and Get Tokens

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123!"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### 4. Refresh Access Token

```bash
curl -X POST "http://127.0.0.1:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### 5. Access Protected Endpoints

```bash
curl -X GET "http://127.0.0.1:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Logout (Blacklist Token)

```bash
curl -X POST "http://127.0.0.1:8000/auth/logout" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_ACCESS_TOKEN"
  }'
```

### 7. Password Reset Flow

**Request reset:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

**Reset password (with token from email):**
```bash
curl -X POST "http://127.0.0.1:8000/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "RESET_TOKEN_FROM_EMAIL",
    "new_password": "NewSecurePass123!"
  }'
```

### 8. Admin Operations

First, manually update a user's role to "admin" in the database, then:

**Get all users:**
```bash
curl -X GET "http://127.0.0.1:8000/users" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

**Change user role:**
```bash
curl -X PUT "http://127.0.0.1:8000/users/1/role" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

**Delete user:**
```bash
curl -X DELETE "http://127.0.0.1:8000/users/1" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## 🏗️ Project Structure

```
user_authentication_system/
├── main.py              # FastAPI application and endpoints
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── database.py          # Database connection and session
├── auth.py              # JWT token creation and verification
├── utils.py             # Password hashing and validation
├── crud.py              # Database CRUD operations
├── dependencies.py      # FastAPI dependencies and middleware
├── security.py          # Security middleware and rate limiting
├── exceptions.py        # Custom exception handlers
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

For production, consider setting these environment variables:

- `SECRET_KEY`: JWT signing secret (change in `auth.py`)
- `DATABASE_URL`: Database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time

### Security Headers

The application automatically adds security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

### CORS Configuration

Configure allowed origins in `security.py`:
```python
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

## 🚨 Error Handling

The system provides comprehensive error handling:

- `400 Bad Request`: Invalid input data, weak password
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: Insufficient permissions (admin required)
- `404 Not Found`: User not found
- `422 Validation Error`: Request validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## 🔍 Security Validations

### Input Validation
- **Username**: 3-20 characters, alphanumeric + underscore only
- **Email**: Valid email format
- **Password**: Minimum 8 characters + 1 special character
- **Input Sanitization**: HTML tag removal and character escaping

### Token Security
- **Access Tokens**: 30-minute expiration
- **Refresh Tokens**: 7-day expiration
- **Token Blacklisting**: Secure logout
- **Token Type Validation**: Prevents token misuse

### Rate Limiting
- **IP-based**: Prevents abuse from single sources
- **Endpoint-specific**: Different limits for different operations
- **Configurable**: Easy to adjust limits in `security.py`

## 🧪 Using the Swagger UI

1. Open `http://127.0.0.1:8000/docs` in your browser
2. Click "Authorize" and enter your JWT token (format: `Bearer YOUR_TOKEN`)
3. Test endpoints directly from the interface
4. View rate limiting information in response headers

## 🚀 Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Configure HTTPS with proper certificates
- [ ] Set up proper CORS origins
- [ ] Configure database with strong credentials
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies
- [ ] Set up email service for password reset

### Performance Considerations
- Use PostgreSQL or MySQL for production
- Implement Redis for rate limiting storage
- Set up connection pooling
- Configure proper logging levels
- Monitor rate limiting effectiveness

## 📝 License

This project is open source and available under the MIT License. 