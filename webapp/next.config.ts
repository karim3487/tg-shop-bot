import type { NextConfig } from "next";

// Derive the production API hostname at build time so Next.js Image can
// fetch thumbnails from MinIO / Django media without crashing.
function getApiHostname(): string | null {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) return null;
  try {
    return new URL(url).hostname;
  } catch {
    return null;
  }
}

const apiHostname = getApiHostname();

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      // Local development (Docker Compose nginx → Django media)
      { protocol: "http", hostname: "localhost", pathname: "/media/**" },
      // MinIO container accessed directly within Docker network
      { protocol: "http", hostname: "minio", port: "9000", pathname: "/**" },
      // Production domain derived from NEXT_PUBLIC_API_URL
      ...(apiHostname && apiHostname !== "localhost"
        ? [
            {
              protocol: "https" as const,
              hostname: apiHostname,
              pathname: "/media/**",
            },
          ]
        : []),
    ],
  },
};

export default nextConfig;
