import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/postcss";
import { fileURLToPath, URL } from "node:url";
import type { Plugin } from "postcss";

function scopeLegacyStyles(): Plugin {
  return { postcssPlugin: "tca-legacy-style-boundary", Once(root) {
    if (!root.source?.input.file?.replaceAll("\\", "/").endsWith("/src/style.css")) return;
    root.walkRules(rule => {
      if (rule.parent?.type === "atrule" && /keyframes$/.test(rule.parent.name)) return;
      rule.selectors = rule.selectors.map(selector => {
        if (/^(:root|html|body)$/.test(selector)) return ".legacy-ui";
        return ":where(.legacy-ui) " + selector;
      });
    });
  } };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  return {
    plugins: [react()],
    css: { postcss: { plugins: [scopeLegacyStyles(), tailwindcss()] } },
    resolve: { alias: {
      "@": fileURLToPath(new URL("./src/cockpit", import.meta.url)),
      "next/link": fileURLToPath(new URL("./src/cockpit/link.tsx", import.meta.url)),
      "next/navigation": fileURLToPath(new URL("./src/cockpit/router.tsx", import.meta.url)),
    } },
    server: { port: 5173, strictPort: true, proxy: { "/api": { target: env.VITE_API_TARGET || "http://127.0.0.1:8765", changeOrigin: false } } },
    build: { outDir: "dist", sourcemap: false },
  };
});
