import { defineConfig, devices } from "@playwright/test";

/**
 * E2E suite against a real running stack (Next.js + FastAPI + Postgres +
 * Redis + S3-compatible storage + a Celery worker). This config
 * deliberately does NOT start any of those services itself (`webServer` is
 * left unset) — orchestrating the full stack is Phase 14's job (Docker
 * Compose); until then, start everything per docs/phase-13-testing.md and
 * point PLAYWRIGHT_BASE_URL / BACKEND_API_BASE_URL at it.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30_000,
  reporter: [["list"]],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        launchOptions: { executablePath: "/opt/pw-browsers/chromium" },
      },
    },
  ],
});
