import path from "node:path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vitest/config"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  test: {
    exclude: ["e2e/**", "node_modules/**", ".next/**"],
    environment: "jsdom",
    globals: true,
    setupFiles: "./vitest.setup.ts",
  },
})
