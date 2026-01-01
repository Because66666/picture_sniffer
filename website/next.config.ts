import type { NextConfig } from "next";

const isDevelopment = process.env.NODE_ENV === 'development';

const nextConfig: NextConfig = {
  output: isDevelopment ? undefined : 'export',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
