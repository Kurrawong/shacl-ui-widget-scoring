import { test } from "@playwright/test";

const URL = "http://localhost:5173/";

test("capture console on load", async ({ page }) => {
  const messages: string[] = [];

  page.on("console", (msg) => {
    messages.push(`${msg.type()}: ${msg.text()}`);
  });

  page.on("pageerror", (err) => {
    messages.push(`pageerror: ${err.message}\n${err.stack}`);
  });

  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(2000);

  console.log("CONSOLE_OUTPUT_START");
  for (const message of messages) {
    console.log(message);
  }
  console.log("CONSOLE_OUTPUT_END");
});
