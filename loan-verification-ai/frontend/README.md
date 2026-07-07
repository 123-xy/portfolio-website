# frontend/ — Next.js 15 / React 19 dashboard

Feature-based structure with the same inward-dependency principle as the
backend, adapted to a frontend. Route files hold no business logic; each
feature owns its domain schemas, API access, components, and hooks.

```
app/                         # Next.js App Router — routes only
  (auth)/login, register
  (applicant)/dashboard, applications
  (officer)/queue, review
  (admin)/users, settings
  layout.tsx, providers.tsx  # (added in Phase 5)
  middleware.ts              # route protection by role (added in Phase 5)

features/
  applications/  verification/  officer-review/
  audit/  reports/  auth/  analytics/
    domain/       # zod schemas + inferred TS types — single source of truth for API contracts
    api/          # typed data-fetching (TanStack Query hooks)
    components/    # feature-specific UI
    hooks/         # feature-specific hooks

shared/
  ui/     # shadcn/ui primitives + design-system wrappers
  lib/    # api client (auth-refreshing fetch), utils
  hooks/  # generic reusable hooks
  types/  # cross-feature shared types
```

Conventions:
- **Zod** schemas in `features/*/domain` validate both React Hook Form
  input and API responses, so a backend contract change fails at the parse
  boundary instead of rendering `undefined`.
- **Server Components** for read-heavy views (queues, reports);
  **Client Components** scoped narrowly to interactive widgets (uploads,
  forms, charts).
- Server state via TanStack Query; local UI state via React state — no
  global client store at this scope.

Strict TypeScript, dark/light mode, responsive, accessible. See
`../../docs/phase-2-architecture-design.md` §3.
