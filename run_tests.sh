#!/bin/bash

# Output color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

# Configuration
COMPOSE_FILE="docker-compose.test.yml"
PROJECT_NAME="django_api_test"
LOG_FILE="test_run.log"

# Test environment configuration (hardcoded for reliability)
export DB_NAME_TEST=test_db
export DB_USER_TEST=test_user
export DB_PASSWORD_TEST=test_password
export DB_HOST_TEST=localhost
export DB_PORT_TEST=5433
export REDIS_URL_TEST=redis://localhost:6380/0
export REDIS_PORT_TEST=6380

# Cleanup function
cleanup() {
    log_warning "Cleaning up..."
    docker-compose -f ${COMPOSE_FILE} down -v --remove-orphans 2>/dev/null
    docker system prune -f 2>/dev/null
    log_success "Cleanup completed"
}

# Trap for cleanup on script exit
trap cleanup EXIT
trap "trap - EXIT; cleanup" INT TERM

# Services check
wait_for_services() {
    log_info "Waiting for services to be ready..."

    # Await Postgres
    local postgres_ready=false
    local attempts=0
    local max_attempts=30

    while [ "$postgres_ready" = false ] && [ $attempts -lt $max_attempts ]; do
        if docker exec postgres_test pg_isready -U ${DB_USER_TEST} -d ${DB_NAME_TEST} >/dev/null 2>&1; then
            postgres_ready=true
            log_success "Postgres is ready"
        else
            attempts=$((attempts + 1))
            log_info "Attempt $attempts/$max_attempts - PostgreSQL not ready..."
            sleep 2
        fi
    done

        if [ "$postgres_ready" = false ]; then
        log_error "PostgreSQL isn't ready after $max_attempts tries"
        return 1
    fi

    # Await Redis
    local redis_ready=false
    attempts=0

    while [ "$redis_ready" = false ] && [ $attempts -lt $max_attempts ]; do
        if docker exec redis_test redis-cli ping >/dev/null 2>&1; then
            redis_ready=true
            log_success "Redis is ready"
        else
            attempts=$((attempts + 1))
            log_info "Attempt $attempts/$max_attempts - Redis not ready..."
            sleep 2
        fi
    done

    if [ "$redis_ready" = false ]; then
        log_error "Redis isn't ready after $max_attempts tries"
        return 1
    fi
}

# Tests execution
run_tests() {
    log_step "Executing tests..."

    # Execute tests with detailed output
    python manage.py test -v 3 --verbosity=3 2>&1 | tee $LOG_FILE
    
    # Get exit code
    TEST_EXIT_CODE=${PIPESTATUS[0]}

    if [ $TEST_EXIT_CODE -eq 0 ]; then
        log_success "Tests completed successfully! 🎉"
    else
        log_error "Some tests failed! 💥"
        log_info "Check the full log in: $LOG_FILE"
    fi

    return $TEST_EXIT_CODE
}

# Check container status function
check_container_status() {
    log_info "Checking container status..."
    docker-compose -f $COMPOSE_FILE ps
}

# Show container logs function
show_container_logs() {
    log_info "Log container PostgreSQL:"
    docker-compose -f $COMPOSE_FILE logs postgres_test | tail -20
    
    log_info "Log container Redis:"
    docker-compose -f $COMPOSE_FILE logs redis_test | tail -20
}

# Main function
main() {
    echo "🧪 ========================================"
    echo "�� DJANGO API TEST SUITE"
    echo "🧪 ========================================"
    echo ""
    
    # 1. Verifica prerequisiti
    log_step "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker isnt installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose isnt installed or not in PATH"
        exit 1
    fi
    
    if ! command -v python &> /dev/null; then
        log_error "Python isnt installed or not in PATH"
        exit 1
    fi
    
    log_success "Prerequisites verified"
    
    # 2. Ferma container esistenti
    log_step "Stopping existing containers..."
    docker-compose -f $COMPOSE_FILE down -v --remove-orphans 2>/dev/null
    log_success "Existing containers stopped"
    
    # 3. Avvia container di test
    log_step "Starting test containers..."
    docker-compose -f $COMPOSE_FILE up -d
    
    if [ $? -ne 0 ]; then
        log_error "Error starting containers"
        exit 1
    fi
    
    log_success "Containers started"
    
    # 4. Mostra stato container
    show_container_status
    
    # 5. Aspetta che i servizi siano pronti
    wait_for_services
    
    # 6. Mostra log container
    show_container_logs
    
    # 7. Esegui test
    run_tests
    TEST_RESULT=$?
    
    # 8. Mostra statistiche
    show_stats
    
    # 9. Cleanup finale
    log_step "Final cleanup..."
    cleanup
    
    # 10. Risultato finale
    if [ $TEST_RESULT -eq 0 ]; then
        echo ""
        echo "🎉 ========================================"
        echo "🎉 ALL TESTS PASSED!"
        echo "🎉 ========================================"
        exit 0
    else
        echo ""
        echo "💥 ========================================"
        echo "�� SOME TESTS FAILED!"
        echo "💥 Check the log: $LOG_FILE"
        echo "💥 ========================================"
        exit 1
    fi
}

# Esegui script
main "$@"