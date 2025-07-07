# padeppoints

This project manages padel tournaments and now features a dual authentication
system powered by [fastapi-users](https://github.com/fastapi-users/fastapi-users).
Users can authenticate via Google OAuth2 or traditional e‑mail/password.

All authentication endpoints are grouped under `/api/v1/auth`.
Refer to `docs/auth_system_design.md` for a complete overview.
