# padeppoints

This project manages padel tournaments and now features a dual authentication
system powered by [fastapi-users](https://github.com/fastapi-users/fastapi-users).
Users can authenticate via Google OAuth2 or traditional e‑mail/password.

See `docs/auth_system_design.md` for details.

## Tournament share links

Organizers can generate a persistent join link for a tournament via
`GET /api/v1/tournaments/{tournament_id}/share-link`. The returned URL
contains a `join_code` query parameter.

Authenticated players can join using this code by sending a `POST` request to
`/api/v1/tournaments/join/{join_code}`. The backend validates the code and adds
the player to the tournament if it is still open for registration.
