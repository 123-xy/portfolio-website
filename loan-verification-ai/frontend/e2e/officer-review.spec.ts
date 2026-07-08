import { expect, test } from "@playwright/test";
import {
  createSubmittedApplication,
  loginOfficer,
  registerApplicant,
  waitForPendingReview,
} from "./support";

/**
 * Requires a real live Celery worker consuming the pipeline queue (see
 * docs/phase-13-testing.md) — the setup submits a real application and waits
 * for the actual AI pipeline to score it, exactly like this project's manual
 * Phase 9-12 verification passes.
 */
test("officer can review evidence, approve, and generate a report through the UI", async ({
  page,
}) => {
  test.setTimeout(90_000);

  const applicant = await registerApplicant(`pw-officer-flow-${Date.now()}@example.com`);
  const applicationId = await createSubmittedApplication(applicant.access_token);
  await waitForPendingReview(applicant.access_token, applicationId);

  await page.goto("/login");
  await page.getByLabel("Email").fill("officer@verifyco.bank");
  await page.getByLabel("Password").fill("OfficerDemo123!");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("**/queue");

  await page.goto(`/review/${applicationId}`);
  await expect(page.getByText("Transcript & findings")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Risk", { exact: false }).first()).toBeVisible();

  await page.getByRole("checkbox").check();
  await page
    .getByPlaceholder("Reason for your decision (required)")
    .fill("Evidence reviewed via Playwright E2E — approving.");
  await page.getByRole("button", { name: "Approve" }).click();

  await expect(page.getByText("Decision recorded")).toBeVisible({ timeout: 10_000 });

  const [reportTab] = await Promise.all([
    page.context().waitForEvent("page", { timeout: 10_000 }),
    page.getByRole("button", { name: "PDF" }).click(),
  ]);
  await reportTab.waitForLoadState();
  expect(reportTab.url()).toContain(".pdf");
  await reportTab.close();
});
