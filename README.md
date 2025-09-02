# Django REST API with JWT Authentication

A modern, production-ready Django REST API featuring JWT authentication, Redis caching, and a clean architecture pattern. This project demonstrates best practices for building scalable APIs with proper separation of concerns.

## 🚀 Features

### Authentication & Security
- **JWT Token-based Authentication** with access and refresh tokens
- **Token Blacklisting** for secure logout and token revocation
- **Password Validation** with Django's built-in validators
- **Secure Token Storage** in Redis with automatic expiration

### Architecture & Design Patterns
- **Repository Pattern** for data access abstraction
- **Service Layer** for business logic separation
- **Dependency Injection** through custom decorators
- **Result Pattern** for consistent error handling
- **Clean Architecture** principles implementation

### Caching & Performance
- **Redis Integration** for session and token management
- **User Session Caching** with configurable TTL
- **Token Storage** with automatic cleanup
- **Connection Pooling** for optimal performance

### Development & Testing
- **Docker Support** for consistent development environment
- **Comprehensive Test Suite** with pytest
- **Environment-based Configuration** (development, testing, production)
- **Logging** with structured error tracking

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
- **Testing**: pytest
- **Python**: 3.13+

## 📋 Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Git

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
# Option 1: Using the provided script
./run_tests.sh

# Option 2: Using pytest directly
pytest

# Option 3: Using Django test command
python manage.py test
```

#### Run Tests with Docker (Recommended)
```bash
# Run tests in isolated Docker environment
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Check test results
docker-compose -f docker-compose.test.yml logs web
```

#### Run Specific Test Categories
```bash
# Run only authentication tests
pytest api/tests.py::TestAuthentication

# Run only service layer tests
pytest api/tests.py::TestUserService

# Run only Redis service tests
pytest api/tests.py::TestRedisService

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=api --cov-report=html
```

### 🧪 **Manual API Testing**

#### 1. **Test User Registration**
```bash
curl -X POST http://localhost:8000/api/account/create/ \
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
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
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

#### 3. **Test Protected Endpoint (User List)**
```bash
# First get the access token from login
ACCESS_TOKEN="your_access_token_here"

curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### 4. **Test Token Refresh**
```bash
REFRESH_TOKEN="your_refresh_token_here"

curl -X POST http://localhost:8000/api/refresh-token/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "'$REFRESH_TOKEN'"
  }'
```

### 🧪 **Testing with Postman/Insomnia**

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

### 🧪 **Testing Redis Operations**

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

#### Monitor Redis Operations
```bash
# Watch Redis operations in real-time
docker-compose exec redis redis-cli monitor

# In another terminal, make API calls to see Redis operations
```

### 🧪 **Database Testing**

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

#### Reset Test Database
```bash
# Drop and recreate test database
docker-compose exec db psql -U test_user -d test_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Run migrations again
docker-compose exec web python manage.py migrate
```

### 🧪 **Performance Testing**

#### Load Testing with Apache Bench
```bash
# Install Apache Bench (if not available)
# Ubuntu/Debian: sudo apt-get install apache2-utils
# macOS: brew install httpd

# Test registration endpoint
ab -n 100 -c 10 -p test_data.json -T application/json http://localhost:8000/api/account/create/

# Test login endpoint
ab -n 100 -c 10 -p login_data.json -T application/json http://localhost:8000/api/login/
```

#### Memory and CPU Monitoring
```bash
# Monitor Docker containers
docker stats

# Monitor specific service
docker stats web redis db
```

### 🧪 **Security Testing**

#### Test Invalid Tokens
```bash
# Test with expired token
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer expired_token_here"

# Test with malformed token
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer invalid_token"

# Test without token
curl -X GET http://localhost:8000/api/users/
```

#### Test Token Blacklisting
```bash
# Login to get tokens
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepassword123"}')

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

# Use token
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Check if token is blacklisted in Redis
docker-compose exec redis redis-cli KEYS "*blacklist*"
```

### 🧪 **Test Coverage Report**

After running tests with coverage:
```bash
# Generate HTML coverage report
pytest --cov=api --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 🧪 **Continuous Integration Testing**

The project is ready for CI/CD with:
- **GitHub Actions**: Use the provided workflow files
- **GitLab CI**: Compatible with GitLab CI/CD
- **Jenkins**: Can be integrated with Jenkins pipelines

**Test Results Summary:**
- ✅ **Unit Tests**: Service layer, repository pattern
- ✅ **Integration Tests**: API endpoints, database operations
- ✅ **Security Tests**: JWT validation, token blacklisting
- ✅ **Performance Tests**: Redis caching, database queries
- ✅ **Manual Tests**: Complete API workflow testing

## 📚 API Endpoints

### Authentication Endpoints

#### User Registration
```http
POST /api/account/create/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}
```

#### User Login
```http
POST /api/login/
Content-Type: application/json

{
    "username": "testuser",
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
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }
}
```

#### Token Refresh
```http
POST /api/refresh-token/
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### User List (Protected)
```http
GET /api/users/
Authorization: Bearer <access_token>
```

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

#### **Local Development (No Docker)**
```env
# Use local PostgreSQL and Redis
SUPABASE_DB_HOST=localhost
SUPABASE_DB_PORT=5432
REDIS_URL=redis://localhost:6379
```

#### **Docker Development (Recommended)**
```env
# Use Docker service names
SUPABASE_DB_HOST=db
SUPABASE_DB_PORT=5432
REDIS_URL=redis://redis:6379
```

#### **Production Environment**
```env
# Use production database and Redis
SUPABASE_DB_HOST=your-production-db.com
SUPABASE_DB_PORT=5432
REDIS_URL=redis://your-production-redis.com:6379
DEBUG=False
```

### Docker Configuration
The project includes two Docker Compose configurations:

- **`docker-compose.yml`**: Development environment
- **`docker-compose.test.yml`**: Testing environment with isolated services

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

### Result Pattern
Consistent error handling across the application:

```python
class Result:
    def __init__(self, success: bool, data=None, error=None):
        self.success = success
        self.data = data
        self.error = error
```

## 🔒 Security Features

- **JWT Token Expiration**: Configurable token lifetimes
- **Token Blacklisting**: Secure logout and token revocation
- **Password Validation**: Django's built-in security validators
- **Redis Security**: Password-protected Redis instances
- **HTTPS Ready**: Configured for production security

## 📊 Performance Features

- **Redis Caching**: User sessions and token storage
- **Connection Pooling**: Optimized database connections
- **Efficient Queries**: Repository pattern for query optimization
- **Background Tasks**: Redis-based task queue ready

## 🚀 Deployment

### Production Considerations
1. Set `DEBUG=False` in production
2. Use environment variables for sensitive data
3. Configure proper logging
4. Set up monitoring and health checks
5. Use HTTPS in production
6. Configure proper CORS settings

### Docker Production
```bash
# Build production image
docker build -t your-app:latest .

# Run with production settings
docker run -e DJANGO_SETTINGS_MODULE=core.settings.production your-app:latest
```

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

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

#### **Redis Connection Issues**
```bash
# Check if Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

#### **Django Application Issues**
```bash
# Check Django logs
docker-compose logs web

# Check Django status
docker-compose exec web python manage.py check

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Clear Django cache
docker-compose exec web python manage.py clearcache
```

#### **Port Conflicts**
```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -an | findstr :8000  # Windows

# Kill process using port
kill -9 <PID>

# Or use different port
docker-compose up -d -p 8001:8000
```

#### **Permission Issues**
```bash
# Fix file permissions
chmod +x run_tests.sh

# Fix Docker permissions (Linux)
sudo chown $USER:$USER . -R
```

#### **Memory Issues**
```bash
# Check Docker memory usage
docker stats

# Clean up Docker
docker system prune -a
docker volume prune
```

#### **Test Failures**
```bash
# Run tests with verbose output
pytest -v -s

# Run specific failing test
pytest api/tests.py::TestClassName::test_method_name -v -s

# Check test database
docker-compose exec db psql -U test_user -d test_db -c "\dt"
```

### Performance Optimization

#### **Database Optimization**
```bash
# Check slow queries
docker-compose exec db psql -U test_user -d test_db -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Analyze table statistics
docker-compose exec web python manage.py dbshell -c "ANALYZE;"
```

#### **Redis Optimization**
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Monitor Redis operations
docker-compose exec redis redis-cli monitor
```

### Debug Mode

#### **Enable Django Debug**
```env
# In .env file
DEBUG=True
LOG_LEVEL=DEBUG
```

#### **Check Logs in Real-time**
```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f web
docker-compose logs -f redis
docker-compose logs -f db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django REST Framework team for the excellent framework
- Redis team for the powerful caching solution
- The Django community for best practices and patterns

## 📞 Support

For questions or support, please open an issue in the GitHub repository.

---

**Built with ❤️ using Django and modern Python practices**
