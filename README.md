# Django REST API with JWT Authentication

A modern, production-ready Django REST API featuring JWT authentication, Redis caching, and a clean architecture pattern. This project demonstrates best practices for building scalable APIs with proper separation of concerns.

## 🚀 Features

### Authentication & Security
- **JWT Token-based Authentication** with access and refresh tokens
- **Token Blacklisting** for secure logout and token revocation (refresh tokens only)
- **Custom Header Support** for refresh tokens (`X-Refresh-Token`)
- **Password Validation** with Django's built-in validators
- **Secure Token Storage** in Redis with automatic expiration

### Architecture & Design Patterns
- **Repository Pattern** for data access abstraction
- **Service Layer** for business logic separation
- **Dependency Injection** through custom decorators
- **Result Pattern** for consistent error handling
- **Clean Architecture** principles implementation

### Caching & Performance
- **Redis Integration** for token blacklisting and session management
- **JTI-based Token Blacklisting** for efficient refresh token invalidation
- **User Session Caching** with configurable TTL
- **Token Storage** with automatic cleanup
- **Basic Connection Pooling** for database connections

### Development & Testing
- **Docker Support** for consistent development environment
- **Basic Test Suite** with Django test framework
- **Environment-based Configuration** (development, testing)
- **Basic Logging** with error tracking

## 🏗️ Project Structure

```
API_django/
├── api/                          # Main application
│   ├── decorators/              # Dependency injection decorators
│   ├── migrations/              # Database migrations
│   ├── models.py                # User model
│   ├── repositories/            # Data access layer
│   ├── serializers/             # Request/response validation
│   ├── services/                # Business logic layer
│   ├── utils/                   # Utility functions
│   ├── urls.py                  # API endpoints
│   └── views.py                 # API views
├── core/                        # Django project settings
├── docker-compose.yml           # Development environment
├── docker-compose.test.yml      # Testing environment
├── requirements.txt             # Python dependencies
└── run_tests.sh                 # Test execution script
```

## 🛠️ Technology Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Containerization**: Docker & Docker Compose
- **Testing**: Django test framework
- **Python**: 3.13+

## 📋 Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Git
- PostgreSQL (if running locally)
- Redis (if running locally)

## 🚀 Quick Start

### 1. Clone and Setup Environment
```bash
git clone <your-repo-url>
cd API_django

# Copy environment file
cp .env.example .env

# Generate new secret key (IMPORTANT: Never use the example key!)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env with your values
nano .env  # or use your preferred editor
```

### 2. Environment Configuration
Create a `.env` file with these variables:
```env
# Django Configuration
SECRET_KEY=your_generated_secret_key_here

# Database Configuration (PostgreSQL)
SUPABASE_DB_NAME=your_database_name
SUPABASE_DB_USER=your_database_user
SUPABASE_DB_PASSWORD=your_database_password
SUPABASE_DB_HOST=your_database_host
SUPABASE_DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password
REDIS_PORT=6379

# Optional: Debug mode (set to False in production)
DEBUG=True
```

### 3. Start Development Environment
```bash
# Start all services (Django + PostgreSQL + Redis)
docker-compose up -d

# Check if services are running
docker-compose ps
```

### 4. Database Setup
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (Optional but recommended for testing)
docker-compose exec web python manage.py createsuperuser
```

### 5. Access the API
- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Browsable API**: Available at all endpoints
- **Health Check**: http://localhost:8000/api/health/ (if implemented)

## 🧪 Testing

### 🧪 **Automated Test Suite**

#### Run All Tests
```bash
# Option 1: Using the provided script (TESTED AND WORKING)
./run_tests.sh

# Option 2: Using Django test command (TESTED AND WORKING)
python manage.py test
```

#### Run Tests with Docker (TESTED AND WORKING)
```bash
# Run tests in isolated Docker environment
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Check test results
docker-compose -f docker-compose.test.yml logs web
```

**Note**: The test environment uses separate ports (PostgreSQL: 5433, Redis: 6380) to avoid conflicts with development services.

### 🧪 **Manual API Testing (THEORETICALLY WORKING)**

#### 1. **Test User Registration**
```bash
curl -X POST http://localhost:8000/api/v1/user/create \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "username": "testuser",
  "email": "test@example.com",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

#### 2. **Test User Login**
```bash
curl -X POST http://localhost:8000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

**Expected Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid-here",
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

#### 3. **Test Public Endpoint (User List)**
```bash
# No authentication required
curl -X GET http://localhost:8000/api/v1/users
```

#### 4. **Test Token Refresh**
```bash
REFRESH_TOKEN="your_refresh_token_here"

curl -X POST http://localhost:8000/api/v1/user/refresh \
  -H "Content-Type: application/json" \
  -H "X-Refresh-Token: $REFRESH_TOKEN"
```

#### 5. **Test User Logout**
```bash
ACCESS_TOKEN="your_access_token_here"
REFRESH_TOKEN="your_refresh_token_here"

curl -X POST http://localhost:8000/api/v1/user/logout \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-Refresh-Token: $REFRESH_TOKEN" \
  -d '{
    "refresh_token": "'$REFRESH_TOKEN'"
  }'
```

**Note**: These curl commands are theoretically correct based on the API implementation, but manual testing with curl has not been performed. The automated tests confirm the API endpoints work correctly.

### 🧪 **Testing with Postman/Insomnia (THEORETICALLY WORKING)**

#### Import this collection:
```json
{
  "info": {
    "name": "Django JWT API Tests",
    "description": "Complete test collection for the Django JWT API"
  },
  "item": [
    {
      "name": "User Registration",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/api/account/create/",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"testuser\",\n  \"email\": \"test@example.com\",\n  \"password\": \"securepassword123\"\n}"
        }
      }
    },
    {
      "name": "User Login",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/api/login/",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"testuser\",\n  \"password\": \"securepassword123\"\n}"
        }
      }
    }
  ]
}
```

**Note**: This Postman collection is provided as a reference but has not been tested. The API endpoints work as confirmed by automated tests.

### 🧪 **Testing Redis Operations (BASIC COMMANDS TESTED)**

#### Check Redis Connection
```bash
# Connect to Redis container
docker-compose exec redis redis-cli

# Test basic operations
127.0.0.1:6379> PING
PONG

127.0.0.1:6379> KEYS *
(empty list or set)

# Exit Redis CLI
127.0.0.1:6379> exit
```

**Note**: Basic Redis operations have been tested. Advanced Redis features (monitoring, memory optimization) have not been tested.

### 🧪 **Database Testing (BASIC COMMANDS TESTED)**

#### Check Database Connection
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U test_user -d test_db

# List tables
\dt

# Check user table
SELECT * FROM api_user;

# Exit PostgreSQL
\q
```

**Note**: Basic database operations have been tested. Advanced database features (performance optimization, query analysis) have not been tested.

### 🧪 **Basic Docker Monitoring (TESTED)**

#### Memory and CPU Monitoring
```bash
# Monitor Docker containers
docker stats

# Monitor specific service
docker stats web redis db
```

**Note**: Basic Docker monitoring commands have been tested. Advanced Docker operations (cleanup, optimization) have not been tested.

**Test Results Summary:**
- ✅ **Automated Tests**: User registration, login, token refresh, logout (TESTED AND WORKING)
- ✅ **Docker Test Environment**: Isolated testing with separate ports (TESTED AND WORKING)
- ✅ **Token Management**: Access token validation, refresh token blacklisting (TESTED AND WORKING)
- ✅ **Custom Headers**: X-Refresh-Token header support (TESTED AND WORKING)
- ✅ **Basic Redis Operations**: Connection and basic commands (TESTED)
- ✅ **Basic Database Operations**: Connection and table queries (TESTED)
- ✅ **Manual API Testing**: All endpoints including logout (THEORETICALLY WORKING - based on automated tests)
- ⚠️ **Advanced Testing**: Performance testing, security testing, coverage reports (NOT TESTED)
- ⚠️ **Production Features**: HTTPS, advanced security, monitoring (NOT TESTED)

## 📚 API Endpoints

### Authentication Endpoints (IMPLEMENTED AND TESTED)

#### User Registration
```http
POST /api/v1/user/create
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}
```

#### User Login
```http
POST /api/v1/user/login
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid-here",
        "username": "testuser",
        "email": "test@example.com"
    }
}
```

#### Token Refresh
```http
POST /api/v1/user/refresh
Content-Type: application/json
X-Refresh-Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### User Logout
```http
POST /api/v1/user/logout
Content-Type: application/json
Authorization: Bearer <access_token>
X-Refresh-Token: <refresh_token>

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Note**: The logout endpoint requires both access token in Authorization header and refresh token in both X-Refresh-Token header and request body.

#### User List (Public - No Authentication Required)
```http
GET /api/v1/users
```

**Note**: All endpoints above are implemented, tested, and working. The API uses UUIDs for user IDs, not integers.

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Configuration
SECRET_KEY=your_generated_secret_key_here

# Database Configuration (PostgreSQL)
SUPABASE_DB_NAME=your_database_name
SUPABASE_DB_USER=your_database_user
SUPABASE_DB_PASSWORD=your_database_password
SUPABASE_DB_HOST=your_database_host
SUPABASE_DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password
REDIS_PORT=6379

# Optional: Debug mode (set to False in production)
DEBUG=True
```

### Environment Setup for Different Scenarios

#### **Docker Development (TESTED AND WORKING)**
```env
# Use Docker service names
SUPABASE_DB_HOST=db
SUPABASE_DB_PORT=5432
REDIS_URL=redis://redis:6379
```

#### **Local Development (NOT TESTED)**
```env
# Use local PostgreSQL and Redis
SUPABASE_DB_HOST=localhost
SUPABASE_DB_PORT=5432
REDIS_URL=redis://localhost:6379
```

#### **Production Environment (NOT TESTED)**
```env
# Use production database and Redis
SUPABASE_DB_HOST=your-production-db.com
SUPABASE_DB_PORT=5432
REDIS_URL=redis://your-production-redis.com:6379
DEBUG=False
```

### Docker Configuration
The project includes two Docker Compose configurations:

- **`docker-compose.yml`**: Development environment (TESTED AND WORKING)
- **`docker-compose.test.yml`**: Testing environment with isolated services (TESTED AND WORKING)

## 🏗️ Architecture Details

### Repository Pattern
The repository pattern abstracts data access logic:

```python
class BaseRepository:
    def __init__(self, model):
        self.model = model
    
    def get_by_id(self, id):
        return self.model.objects.get(id=id)
```

### Service Layer
Business logic is encapsulated in service classes:

```python
class UserService:
    def __init__(self, user_repository, redis_service):
        self.user_repository = user_repository
        self.redis_service = redis_service
```

### Dependency Injection
Custom decorators handle dependency injection:

```python
@service_injector(UserService)
@serializer_injector(UserSerializer)
def account_create(request, service, serializer):
    # Dependencies are automatically injected
```

### Token Management
Custom decorators for JWT token handling:

```python
@route_protector(pass_token=True)  # Validates and passes access token
@extract_refresh_token()           # Extracts refresh token from X-Refresh-Token header
def logout(request, service, access_token, refresh_token):
    # Both tokens are automatically validated and injected
```

### Result Pattern
Consistent error handling across the application:

```python
class Result:
    def __init__(self, success: bool, data=None, error=None):
        self.success = success
        self.data = data
        self.error = error
```

**Note**: All architecture patterns shown above are implemented and tested in the codebase.

## 🔒 Security Features

- **JWT Token Expiration**: Configurable token lifetimes
- **Token Blacklisting**: Secure logout and token revocation (refresh tokens only)
- **JTI-based Blacklisting**: Efficient token invalidation using JWT ID
- **Custom Header Authentication**: Refresh tokens via `X-Refresh-Token` header
- **Password Validation**: Django's built-in security validators
- **Basic Redis Security**: Redis instance configuration
- **Development Security**: Basic security measures implemented

## 📊 Performance Features

- **Redis Caching**: User sessions and token blacklisting
- **JTI-based Token Management**: Efficient refresh token invalidation
- **Basic Connection Pooling**: Database connection optimization
- **Repository Pattern**: Clean data access abstraction
- **Token Management**: Efficient JWT token handling with custom decorators

## 🚀 Deployment

### Production Considerations (NOT TESTED)
1. Set `DEBUG=False` in production
2. Use environment variables for sensitive data
3. Configure proper logging
4. Set up monitoring and health checks
5. Use HTTPS in production
6. Configure proper CORS settings

### Docker Production (NOT TESTED)
```bash
# Build production image
docker build -t your-app:latest .

# Run with production settings
docker run -e DJANGO_SETTINGS_MODULE=core.settings.production your-app:latest
```

**Note**: Production deployment has not been tested. This is a development-ready project that needs production configuration.

## 🔧 Troubleshooting

### Common Issues and Solutions

#### **Database Connection Issues**
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test database connection
docker-compose exec web python manage.py dbshell
```

#### **Redis Connection Issues**
```bash
# Check if Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### **Django Application Issues**
```bash
# Check Django logs
docker-compose logs web

# Check Django status
docker-compose exec web python manage.py check
```

#### **Port Conflicts**
```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -an | findstr :8000  # Windows

# Or use different port
docker-compose up -d -p 8001:8000
```

#### **Basic Docker Monitoring**
```bash
# Check Docker memory usage
docker stats

# Monitor specific service
docker stats web redis db
```

### Debug Mode

#### **Check Logs in Real-time**
```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f web
docker-compose logs -f redis
docker-compose logs -f db
```

**Note**: Advanced troubleshooting commands (performance optimization, advanced database operations) have not been tested and may require additional packages or configurations.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

**Note**: This project currently doesn't have a license file. If you want to add one, you can:
- Create a `LICENSE` file with MIT, Apache 2.0, or GPL license
- Or remove this section entirely

## 🙏 Acknowledgments

- Django REST Framework team for the excellent framework
- Redis team for the powerful caching solution
- The Django community for best practices and patterns
- **Note**: This project demonstrates learned concepts and best practices from the Django ecosystem

## 📞 Support

For questions or support, please open an issue in the GitHub repository.

---

**Built with ❤️ using Django and modern Python practices**

**Project Status**: Development-ready with comprehensive testing. Production deployment requires additional configuration and testing.
