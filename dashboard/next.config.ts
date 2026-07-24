import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit a self-contained server (server.js + trimmed node_modules) so the
  // Docker runner stage stays small and needs no install step.
  output: "standalone",
  // The dashboard sits in a subfolder of the repo; without pinning the
  // tracing root Next walks up the tree and nests server.js deep under
  // .next/standalone/<ancestor path>. Pin it here so server.js lands at
  // .next/standalone/server.js where the Dockerfile expects it.
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
