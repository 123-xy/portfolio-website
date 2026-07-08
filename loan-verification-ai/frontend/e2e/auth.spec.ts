import { expect, test } from "@playwright/test";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`;
}

test("registering a new account lands on the applicant dashboard", async ({ page }) => {
  await page.goto("/register");

  await page.getByLabel("Full name").fill("Playwright User");
  await page.getByLabel("Email").fill(uniqueEmail("pw-register"));
  await page.getByLabel("Password", { exact: true }).fill("Str0ngPass!234");
  await page.getByLabel("Confirm password").fill("Str0ngPass!234");
  await page.getByRole("button", { name: "Create account" }).click();

  await page.waitForURL("**/dashboard");
  await expect(page.getByText("Approved", { exact: false }).first()).toBeVisible({ timeout: 10_000 });
});

test("registering with an email already in use shows an error", async ({ page }) => {
  const email = uniqueEmail("pw-dupe");

  await page.goto("/register");
  await page.getByLabel("Full name").fill("Playwright User");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password", { exact: true }).fill("Str0ngPass!234");
  await page.getByLabel("Confirm password").fill("Str0ngPass!234");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/dashboard");

  await page.goto("/register");
  await page.getByLabel("Full name").fill("Playwright User Again");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password", { exact: true }).fill("Str0ngPass!234");
  await page.getByLabel("Confirm password").fill("Str0ngPass!234");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.getByText("already exists")).toBeVisible();
  await expect(page).toHaveURL(/\/register/);
});

test("logging in with the wrong password shows an error and does not navigate away", async ({
  page,
}) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("nobody-at-all@example.com");
  await page.getByLabel("Password").fill("WrongPass!234");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page.getByText("Invalid email or password.")).toBeVisible();
  await expect(page).toHaveURL(/\/login/);
});
