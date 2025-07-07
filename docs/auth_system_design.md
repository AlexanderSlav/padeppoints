# Authentication System Design

This document describes the authentication system built with `fastapi-users`.

## Architecture Overview

```
Client --> FastAPI --> fastapi-users --> Database
                        |-- Google OAuth2
```

- **fastapi-users** handles both JWT authentication and OAuth2 flows.
- Users can sign up with email/password or via Google OAuth2.
- All user data is stored in the `users` table.

## Components

- **UserManager** – custom manager integrating with SQLAlchemy.
- **Authentication Backend** – JWT bearer tokens.
- **GoogleOAuth2 Client** – provided by `httpx-oauth`.

## Database Schema Changes

Two fields were added to the `users` table:

- `hashed_password`: stores bcrypt hashed passwords.
- `is_verified`: indicates whether the email is verified.

See migration `b4a1b4c3c9bd_add_auth_fields_to_user.py`.

## API Endpoints

- `POST /api/v1/auth/register` – create account with email/password.
- `POST /api/v1/auth/jwt/login` – obtain JWT token.
- `POST /api/v1/auth/reset/request` – request password reset.
- `POST /api/v1/auth/reset/confirm` – confirm password reset with token.
- `POST /api/v1/auth/verify/request` – request verification e‑mail.
- `POST /api/v1/auth/verify/confirm` – confirm verification.
- `GET  /api/v1/auth/google/authorize` – start Google OAuth flow.
- `GET  /api/v1/auth/google/callback` – OAuth callback.
- `GET  /api/v1/auth/users/me` – get current authenticated user.

## Implementation Plan

1. Added `fastapi-users` and `httpx-oauth` dependencies.
2. Extended `User` model and created Alembic migration for new fields.
3. Implemented `UserManager` and authentication backend.
4. Replaced legacy auth routes with `fastapi-users` routers.
5. Created dependencies helpers using `fastapi-users`.
6. Updated application configuration and OpenAPI documentation.

## Testing Strategy

Authentication routes can be exercised using unit tests with HTTPX.
Both Google OAuth and email/password flows rely on `fastapi-users` which provides
extensive test coverage. Custom logic should be tested with mocked requests.
