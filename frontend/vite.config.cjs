const { defineConfig } = require("vite");

const apiInternalPort = process.env.API_INTERNAL_PORT || "8000";
const apiProxyTarget = process.env.API_PROXY_TARGET || `http://localhost:${apiInternalPort}`;
const frontendInternalPort = Number(process.env.FRONTEND_INTERNAL_PORT || "5173");

const proxiedApiRoutes = ["/api", "/health", "/docs", "/openapi.json", "/redoc"];

const proxy = Object.fromEntries(
  proxiedApiRoutes.map((route) => [
    route,
    {
      target: apiProxyTarget,
      changeOrigin: true,
    },
  ]),
);

module.exports = defineConfig({
  server: {
    host: "0.0.0.0",
    port: frontendInternalPort,
    strictPort: true,
    watch: {
      usePolling: true,
    },
    proxy,
  },
});
