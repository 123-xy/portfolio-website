# Phase 7 — Authentication

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — verified end-to-end through the real UI against the live backend.
**Depends on:** Phases 1–6.

> Implements register / login / refresh / logout / current-user with Argon2id
> password hashing, JWT access tokens, rotating hashed refresh tokens with
> server-side revocation, brute-force lockout, and RBAC — then wires the
> frontend forms to the real endpoints with token storage, transparent
> refresh, and route guards.

## Backend

**Clean-architecture flow** (ports → use cases → infrastructure → interface):
- **Domain entities**: `User`, `RefreshToken` — persistence-independent, with
  `is_locked()` / `is_active()` invariants.
- **Ports**: `UserRepository`, `RefreshTokenRepository`, `PasswordHasher`,
  `TokenService` — abstract interfaces the use cases depend on.
- **Use cases**: `RegisterUser`, `AuthenticateUser` (lockout), `RefreshAccessToken`
  (rotation), `LogoutUser`, and a shared `TokenIssuer`.
- **Infrastructure**: `Argon2PasswordHasher`, `JwtTokenService` (HS256 access
  tokens + opaque SHA-256-hashed refresh tokens), and SQLAlchemy repositories
  mapping ORM ⇄ domain entities.
- **Interface**: `/auth/register`, `/auth/login`, `/auth/refresh`,
  `/auth/logout`, `/auth/me`; `get_current_user` and a `require_role(...)`
  RBAC dependency factory.

**Security properties (all verified):**
- Passwords stored as Argon2id (`$argon2id$v=19$…`), never plaintext.
- Refresh tokens stored only as SHA-256 hashes; rotation revokes the old token
  and links the chain (`replaced_by`), so a used/stolen refresh token cannot be
  replayed.
- Generic "Invalid email or password" for both missing user and wrong password
  (no user enumeration).
- Configurable brute-force lockout (default 5 attempts → 15-minute lock).
- Self-registration is applicant-only; privileged roles are provisioned by an
  admin.
- Request-scoped transaction: one request = one atomic commit (the session
  dependency commits on success, rolls back on error).

**Also fixed this phase:** all `datetime` columns are now `TIMESTAMPTZ`
(mapped globally via the Base `type_annotation_map`) — timezone-correct storage
is a must for an audit- and retention-driven banking system. The initial
migration was regenerated accordingly (parity re-verified).

## Frontend

- `auth-tokens.ts` — localStorage token store (documented trade-off; httpOnly
  cookies are a noted production hardening step).
- `api-client` wired to attach the bearer token and transparently refresh once
  on a 401 via the backend rotate endpoint.
- `auth-api.ts` — register/login/logout/me, mapping the backend's snake_case to
  the app's camelCase at the boundary via Zod.
- Hooks: `useCurrentUser`, `useAuthGuard`, `useLogout`, `homeRouteForRole`.
- Login/register forms call the real API, store tokens, surface server errors
  (401 → invalid credentials, 409 → email exists), and route by role.
- `AuthGuard` wraps the applicant and officer route groups; profile shows the
  live user from `/auth/me` and signs out for real.

## Verification performed

- **Backend, live PostgreSQL 16 + Redis**: full curl walkthrough — register
  (201 + tokens), `/me` (correct user), missing-token (401 envelope),
  duplicate (409), wrong password (401 generic), login, refresh (rotates),
  old-refresh-after-rotation (401), logout (204), weak password (422). DB
  inspection confirmed Argon2 hashes and the 2-active/2-revoked/1-chained
  refresh-token state.
- **Full-stack, headless Chromium against the running app**: register through
  the UI → dashboard + token stored → profile shows the real email from
  `/auth/me` → sign out clears the token and redirects → guard redirects a
  logged-out user off `/dashboard` → log back in through the UI.
- **Quality gates**: backend `ruff` clean, `mypy --strict` clean (app),
  `pytest` 16/16 (token service, use-case lockout/rotation/enumeration logic,
  models, health); migration parity holds. Frontend `tsc` clean, `next build`
  compiles all routes.

## Deferred (to their phases)

- Seed migration for the initial admin user + active `risk_engine_config`
  (Phase 14 / alongside admin features).
- Audit-log writes for auth events (once the audit service lands, Phase 8+).
- httpOnly-cookie refresh-token storage hardening (production).
- Full API integration tests against ephemeral Postgres (Phase 13).
