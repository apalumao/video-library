import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  basePath: '/video-library',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
