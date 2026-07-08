import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`;
}

/** Real, valid tiny fixture files (not empty/random bytes) so the browser's
 * own file-picker and the app's `accept` filters behave exactly as they
 * would for a real user. */
const FIXTURES_DIR = path.join(__dirname, "fixtures");

test("applicant can create an application, upload all artifacts through the UI, and submit", async ({
  page,
}) => {
  await page.goto("/register");
  await page.getByLabel("Full name").fill("Playwright Applicant");
  await page.getByLabel("Email").fill(uniqueEmail("pw-upload"));
  await page.getByLabel("Password", { exact: true }).fill("Str0ngPass!234");
  await page.getByLabel("Confirm password").fill("Str0ngPass!234");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/dashboard");

  await page.goto("/applications/new");
  await page.getByLabel("Loan amount (₹)").fill("1500000");
  await page.getByLabel("Purpose (optional)").fill("Home renovation");
  await page.getByLabel("Co-applicant name").fill("Playwright Co-Applicant");
  await page.getByRole("button", { name: "Create & continue to upload" }).click();

  await page.waitForURL(/\/applications\/[0-9a-f-]+$/);
  await expect(page.getByText("Verification artifacts")).toBeVisible();

  const fileInputs = page.locator('input[type="file"]');
  await expect(fileInputs).toHaveCount(3);
  await fileInputs.nth(0).setInputFiles(path.join(FIXTURES_DIR, "photo.jpg"));
  await expect(page.getByText("Uploaded").first()).toBeVisible({ timeout: 10_000 });
  await fileInputs.nth(1).setInputFiles(path.join(FIXTURES_DIR, "photo.jpg"));
  await fileInputs.nth(2).setInputFiles(path.join(FIXTURES_DIR, "video.mp4"));
  await expect(page.getByText("Uploaded")).toHaveCount(3, { timeout: 10_000 });

  const submitButton = page.getByRole("button", { name: "Submit for verification" });
  await expect(submitButton).toBeEnabled();
  await submitButton.click();

  await expect(page.getByText("still processing", { exact: false })).toBeVisible({
    timeout: 10_000,
  });
});
