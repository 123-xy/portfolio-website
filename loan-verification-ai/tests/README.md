# tests/ — Cross-service end-to-end tests

Tests that exercise multiple services together (frontend → backend →
worker → storage). Service-local unit and integration tests live inside
each service (`backend/tests/`, `ai-services/tests/`,
`frontend/features/*` colocated tests).

```
e2e/   # full-journey tests: applicant submits → pipeline runs → officer decides
```

The Phase-1 "Definition of Done" happy path and the key rejection paths
are the primary e2e scenarios (see `../../docs/phase-1-requirements-analysis.md` §7).
Implemented in Phase 13.
