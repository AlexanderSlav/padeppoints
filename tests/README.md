# Tournament System Tests

This directory contains comprehensive tests for the Padel Tournament System.

## Test Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for API endpoints and database interactions
- `conftest.py` - Pytest configuration and fixtures

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=app --cov-report=html
```

### Run Specific Test Files
```bash
# Test tournament service
pytest tests/unit/test_tournament_service.py

# Test Americano service
pytest tests/unit/test_americano_service.py

# Test API endpoints
pytest tests/integration/test_tournament_api.py

# Test database interactions
pytest tests/integration/test_database.py
```

## Test Coverage

The tests cover:

### Unit Tests
- **Tournament Service**: Tournament creation, starting, round advancement, scoring
- **Americano Service**: Round generation, score calculation, winner determination
- **Format Services**: Validation, round calculation, tournament completion

### Integration Tests
- **API Endpoints**: All tournament-related endpoints
- **Database Operations**: CRUD operations, relationships, transactions
- **Tournament Flow**: Complete tournament lifecycle from creation to completion

## Test Database

Tests use an in-memory SQLite database for fast, isolated testing. Each test gets a fresh database session that's automatically rolled back after the test completes.

## Configuration

Test configuration is managed through:
- `pytest.ini` - Pytest settings
- `conftest.py` - Test fixtures and database setup
- Environment variables for database DSN override

## Database DSN Configuration

You can configure the database connection using environment variables:

```bash
# Individual database components
export DB_HOSTNAME=localhost
export DB_PORT=5432
export DB_USERNAME=postgres
export DB_PASSWORD=password
export DB_NAME=padel_tournaments

# Or use a complete DSN
export DATABASE_DSN=postgresql+asyncpg://user:pass@host:port/dbname
```

The `DATABASE_DSN` environment variable takes precedence over individual components.

## Test Fixtures

Key fixtures available:
- `test_user` - A regular test user
- `test_organizer` - A tournament organizer user
- `test_players` - List of 8 test players for tournaments
- `test_tournament` - A complete tournament with players
- `db_session` - Database session for testing

## Writing New Tests

When adding new tests:

1. Use appropriate test markers (`@pytest.mark.asyncio` for async tests)
2. Use existing fixtures when possible
3. Follow the naming convention `test_*`
4. Add docstrings explaining what the test does
5. Test both success and failure cases
6. Mock external dependencies appropriately

## Example Test

```python
@pytest.mark.asyncio
async def test_my_feature(db_session: AsyncSession, test_tournament: Tournament):
    """Test my new feature."""
    # Arrange
    service = MyService(db_session)
    
    # Act
    result = await service.my_method(test_tournament.id)
    
    # Assert
    assert result is not None
    assert result.status == "expected_status"
```