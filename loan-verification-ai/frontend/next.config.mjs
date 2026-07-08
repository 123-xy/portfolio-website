/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Emit a self-contained server bundle (.next/standalone) so the production
  // Docker image ships only the traced runtime dependencies, not the full
  // node_modules tree — see docker/Dockerfile.frontend.
  output: "standalone",
  eslint: {
    // Lint is run as a dedicated CI step, not coupled to the production build.
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
