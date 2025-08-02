# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a padel tournament management system with a FastAPI backend and React frontend. The system supports dual authentication (Google OAuth2 and email/password) via fastapi-users and manages tournament creation, player registration, match scheduling, and scoring for different tournament formats (currently Americano, with Mexicano planned).

## Development Commands

### Docker Development (Primary Method)
- `make dev-full` - Start full stack in development mode (backend + frontend + database)
- `make dev` - Start backend services only (database + API) with hot reloading
- `make dev-frontend` - Start frontend only in development mode
- `make up` - Start all services in production mode
- `make down` - Stop all containers
- `make logs` - Show logs for all services
- `make logs-backend` - Show backend logs only
- `make logs-frontend` - Show frontend logs only

### Database Operations
- `make migration m="description"` - Create new Alembic migration
- `make fix-migration-sync` - Run migrations to sync database
- `make migration-status` - Check current migration status
- `make reset-db` - Reset database completely (DEV ONLY - LOSES DATA!)
- `make connect-db` - Connect to PostgreSQL container

### Testing
- `make test` - Run all tests in Docker container
- `make test-unit` - Run only unit tests
- `make test-integration` - Run only integration tests
- `make test-coverage` - Run tests with coverage report

### Container Access
- `make connect-backend` - Connect to backend container bash
- `make connect-frontend` - Connect to frontend container shell

## Architecture

### Backend Structure (FastAPI)
- **Models** (`app/models/`): SQLAlchemy ORM models for database entities
- **Repositories** (`app/repositories/`): Data access layer with CRUD operations
- **Services** (`app/services/`): Business logic layer
  - `TournamentService`: Main coordinator for tournament operations
  - `AmericanoTournamentService`: Americano format-specific logic
  - `BaseTournamentFormat`: Abstract base for tournament formats
- **API Endpoints** (`app/api/v1/endpoints/`): FastAPI route handlers
- **Schemas** (`app/schemas/`): Pydantic models for request/response validation
- **Core** (`app/core/`): Authentication, configuration, dependencies

### Frontend Structure (React)
- **Pages** (`padel-frontend/src/pages/`): Main application views
- **Components** (`padel-frontend/src/components/`): Reusable UI components
- **Services** (`padel-frontend/src/services/`): API communication layer
- **AuthContext**: React context for user authentication state

### Database
- PostgreSQL with SQLAlchemy async ORM
- Alembic for database migrations
- Tables: users, tournaments, rounds, tournament_player

### Authentication System
- Powered by fastapi-users library
- Dual authentication: Google OAuth2 and email/password
- JWT bearer tokens for session management
- See `docs/auth_system_design.md` for detailed architecture

## Tournament System Architecture

### Tournament Formats
The system uses a pluggable tournament format architecture:
- `BaseTournamentFormat`: Abstract base class defining the interface
- `AmericanoTournamentService`: Implements Americano tournament logic
- `TournamentService`: Main coordinator that delegates to format-specific services

### Tournament Lifecycle
1. **PENDING**: Tournament created, players can join
2. **ACTIVE**: Tournament started, rounds generated, matches being played
3. **COMPLETED**: Tournament manually finished by organizer

### Key Business Rules
- Tournaments are manually finished by organizers (not automatically after last round)
- Result editing is disabled once tournament is completed
- Americano format: team scores must sum to points_per_match value
- Minimum 4 players required to start a tournament

## Testing Strategy

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test API endpoints with database
- Tests use pytest with async support
- Test database setup handled in `conftest.py`
- Use `pytest-mock` for mocking dependencies

## Key Configuration

### Environment Variables
Required in `.env` file:
- Database connection: `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`
- Authentication: Google OAuth2 credentials
- JWT secret keys

### Development Ports
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000  
- PostgreSQL: localhost:5432

## Development Standards

### Code Quality Requirements
- **Modular Design**: Break functionality into clear services/components/modules. Avoid tight coupling
- **Readable Code**: Use descriptive variable/function names, keep logic blocks small and focused
- **Reusability**: Use shared utilities instead of duplicating logic
- **Testing**: All new logic requires test coverage (unit tests for components, integration tests for workflows)
- **Documentation**: Every new feature must include documentation updates

### Security & Privacy
- **Input Validation**: All user inputs and external API data must be validated using Pydantic schemas
- **Access Control**: Verify permission checks for authenticated endpoints using dependencies
- **Sensitive Data**: Never log tokens, emails, or sensitive user data

### Performance Best Practices
- **Database Queries**: Avoid N+1 patterns, use SQLAlchemy's `selectinload` for related data
- **Async Operations**: Long-running tasks should use async patterns properly
- **Caching**: Consider caching for static/frequently accessed data

### Git & Pull Request Standards
- **Commits**: Use clear, imperative messages (e.g., "Fix tournament status update", "Add user search endpoint")
- **PRs**: Keep focused and single-purpose, include description of what changed and why
- **Testing**: All PRs must pass CI including type checking and test suites

## Common Development Patterns

### Adding New Tournament Format
1. Create new service class inheriting from `BaseTournamentFormat`
2. Implement required abstract methods: `generate_rounds()`, `calculate_player_scores()`, etc.
3. Register in `TournamentService.FORMAT_SERVICES` dictionary
4. Add corresponding enum value to `TournamentSystem`

### Creating API Endpoints
1. Add route handler in appropriate endpoint file (`app/api/v1/endpoints/`)
2. Define request/response schemas in `app/schemas/`
3. Use dependency injection for database sessions and authentication
4. Follow existing patterns for error handling and validation

### Database Changes
1. Modify SQLAlchemy models in `app/models/`
2. Create migration: `make migration m="description"`
3. Review generated migration file in `alembic/versions/`
4. Apply migration: `make fix-migration-sync`