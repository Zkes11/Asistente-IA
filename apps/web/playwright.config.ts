import { defineConfig, devices } from "@playwright/test";

const webPort = Number(process.env.PLAYWRIGHT_WEB_PORT ?? 3002);
const apiPort = Number(process.env.PLAYWRIGHT_API_PORT ?? 8002);

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 45_000,
  retries: 0,
  use: {
    baseURL: `http://127.0.0.1:${webPort}`,
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: `py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port ${apiPort}`,
      cwd: "../api",
      env: {
        WEB_ORIGIN: `http://127.0.0.1:${webPort}`,
      },
      url: `http://127.0.0.1:${apiPort}/api/v1/health`,
      reuseExistingServer: true,
      timeout: 180_000,
    },
    {
      command: `npm run dev --workspace web -- --hostname 127.0.0.1 --port ${webPort}`,
      cwd: "../..",
      env: {
        NEXT_PUBLIC_API_URL: `http://127.0.0.1:${apiPort}/api/v1`,
      },
      url: `http://127.0.0.1:${webPort}`,
      reuseExistingServer: true,
      timeout: 180_000,
    },
  ],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
