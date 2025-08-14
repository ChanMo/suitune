import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    react({
      include: "**/*.{jsx,tsx,js}",
    }),
  ],
  server: {
    port: 5173,
  },
  esbuild: {
    loader: "jsx",
    include: /src\/.*\.js$/,
  },
});
