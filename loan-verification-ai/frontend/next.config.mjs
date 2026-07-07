/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  eslint: {
    // Lint is run as a dedicated CI step, not coupled to the production build.
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
