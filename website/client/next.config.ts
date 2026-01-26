import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  basePath: '/video-library',
  assetPrefix: '/video-library/',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
