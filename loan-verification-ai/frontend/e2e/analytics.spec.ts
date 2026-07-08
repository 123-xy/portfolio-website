import { expect, test } from "@playwright/test";

test("officer analytics dashboard renders live data and bulk export works", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("officer@verifyco.bank");
  await page.getByLabel("Password").fill("OfficerDemo123!");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("**/queue");

  await page.goto("/analytics");
  await expect(page.getByText("Total applications")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByText("Approval rate")).toBeVisible();
  await expect(page.getByText("Approved", { exact: true }).first()).toBeVisible();

  // A CSV response isn't renderable inline, so Chromium treats the new tab
  // as a download rather than a navigable page — wait for the download
  // event, not `page`/`waitForLoadState` (see PDF-report tests for the
  // renderable-content case, which does open as a normal tab).
  const [download] = await Promise.all([
    page.context().waitForEvent("download", { timeout: 10_000 }),
    page.getByRole("button", { name: "CSV", exact: true }).click(),
  ]);
  expect(download.url()).toContain(".csv");
});
