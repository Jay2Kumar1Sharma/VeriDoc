import { test, expect } from "@playwright/test"

test.beforeEach(async () => {
  try {
    const response = await fetch("http://localhost:8000/health")
    test.skip(!response.ok, "Backend is unavailable")
  } catch {
    test.skip(true, "Backend is unavailable")
  }
})

test("asks a question and opens a citation drawer", async ({ page }) => {
  await page.goto("/")
  await page.getByLabel("Ask a question").fill("How do path parameters work?")
  await page.getByLabel("Send").click()
  await expect(page.getByText(/\[#|chunk/i)).toBeVisible({ timeout: 30000 })
  const citation = page.getByRole("button", { name: /open citation/i }).first()
  await citation.click()
  await expect(page.getByText(/Citation|chunk/i)).toBeVisible()
})

