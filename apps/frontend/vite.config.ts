import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development the browser talks to Vite, which proxies /api to the local backend (uvicorn on :8000
// or a kubectl port-forward). In production nginx does the same proxying (see nginx.conf).
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { "/api": process.env.BACKEND_URL || "http://localhost:8000" } },
});
