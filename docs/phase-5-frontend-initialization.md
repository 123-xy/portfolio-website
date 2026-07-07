# Phase 5 — Frontend Initialization

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — builds, typechecks, and serves.
**Depends on:** Phases 1–4.

> First phase with runnable code. Establishes the Next.js 15 / React 19 /
> TypeScript frontend as a **mobile-app experience** — a phone-style app
> shell with fixed bottom tab navigation, a sticky top app bar, touch-first
> controls, card-based content, Framer Motion transitions, and dark/light
> theming.

## What shipped

**Toolchain & config**
- `package.json` — Next.js 15.5 (patched past CVE-2025-66478), React 19,
  TypeScript 5.7, Tailwind 3.4, Framer Motion, React Hook Form, Zod,
  TanStack Query, next-themes, lucide-react, class-variance-authority.
- Strict TypeScript (`strict`, `noUncheckedIndexedAccess`,
  `noImplicitOverride`, `noFallthroughCasesInSwitch`), `@/*` path alias.
- Tailwind theme tokens (HSL CSS variables) for a premium banking palette in
  both light and dark; `globals.css` adds the phone-frame, safe-area insets,
  and native scroll behavior.

**Mobile app shell** (`shared/ui/shell/`)
- `AppShell` — top app bar + scrollable content + optional bottom tab bar.
- `AppBar` — sticky, safe-area-aware header with optional back button and
  trailing actions.
- `BottomNav` — fixed tab bar with a Framer Motion shared-layout active pill;
  resolves its own item list from a serializable `persona` string so icon
  components never cross the RSC boundary.
- `PageTransition` — subtle native-feeling screen-push animation.
- Phone frame: full-bleed on mobile, centered device frame on desktop.

**Shared foundation** (`shared/`)
- `lib/api-client.ts` — typed fetch wrapper with bearer auth, JSON handling,
  normalized `ApiError`, and one transparent 401 refresh-and-retry (token
  storage is injected, so it is testable and wires to real auth in Phase 7).
- `lib/env.ts` — Zod-validated public runtime config.
- UI primitives (shadcn-style, hand-authored): `Button`, `Card`, `Badge`,
  `Input`, `Label`, `ThemeToggle` — all with ≥44px tap targets.

**Screens & routing** (`app/`)
- Route groups by persona: `(auth)`, `(applicant)`, `(officer)`.
- Welcome/splash, login, register (React Hook Form + Zod validation).
- Applicant: dashboard (hero CTA, stat tiles, recent applications),
  applications list, application detail, new-application step layout,
  profile.
- Officer: verification queue, analytics KPIs.
- `not-found` screen.

**Feature modules** (`features/`)
- `auth/` — Zod schemas as the single contract source, login/register forms.
- `applications/` — status/risk presentation metadata, `ApplicationCard`,
  and fixture data (a single file, swapped for real TanStack Query hooks in
  Phase 8).

## Verification performed

- `tsc --noEmit` — clean.
- `next build` — succeeds; all 12 routes compile (static + one dynamic).
- Production server smoke test — every route returns 200 and renders its
  expected content, including the dynamic `/applications/[id]`.
- Visual check via headless Chromium at a mobile viewport (402×874) in both
  light and dark — confirms the app-shell, bottom nav active pill, cards, and
  theming render correctly.

## Deliberately deferred (to their proper phases)

- Real auth/token exchange → Phase 7 (forms currently validate then route).
- Live data via API hooks (replacing fixtures) → Phase 8+.
- Upload flow, officer decision actions, analytics charts, admin screens →
  Phases 8, 11, 12.
- Frontend unit/component tests → Phase 13.
