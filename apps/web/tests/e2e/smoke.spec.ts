import { expect, test } from "@playwright/test";

test("analisis por chat y plan personalizado desde la navegacion", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: /habla primero, analiza despues/i })).toBeVisible();
  await expect(page.getByText(/primero conversemos/i)).toBeVisible();

  await page.goto("/chat");
  await expect(page).toHaveURL(/\/chat$/);
  await expect(page.getByRole("heading", { name: /conversemos antes de decidir/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /nueva conversacion/i })).toBeVisible();
  await page.getByRole("button", { name: /nueva conversacion/i }).click();
  await page.getByRole("button", { name: /comenzar analisis/i }).click();

  const textarea = page.getByPlaceholder(/escribe con libertad/i);
  const answers = [
    "Me interesa la tecnologia, crear apps y resolver problemas logicos.",
    "Disfruto mucho analizar problemas y me siento comodo con la logica.",
    "Prefiero aprender haciendo proyectos y probando herramientas.",
    "Tambien me gusta trabajar con datos y encontrar patrones.",
    "Quiero un trabajo donde construya soluciones digitales utiles.",
  ];

  for (const answer of answers) {
    await textarea.fill(answer);
    await page.getByRole("button", { name: /enviar respuesta/i }).click();
  }

  await expect(page.getByRole("button", { name: /procesar analisis/i })).toBeVisible();
  await page.getByRole("button", { name: /procesar analisis/i }).click();

  await expect(page.getByRole("button", { name: /abrir plan/i })).toBeVisible({ timeout: 20000 });
  await page.getByRole("button", { name: /abrir plan/i }).click();

  await expect(page).toHaveURL(/\/action-plan$/);
  await expect(page.getByText(/este plan se arm[oó] desde lo que respondiste en el chat/i)).toBeVisible();
  await expect(page.locator("main")).toContainText(/me interesa la tecnologia/i);
  await expect(page.locator("main")).toContainText(/estudiar primero/i);
});
