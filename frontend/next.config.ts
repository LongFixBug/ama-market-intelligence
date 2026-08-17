import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The in-app browser uses 127.0.0.1 while Next's dev server advertises
  // localhost. Keep this allowlist local-only so the dev chunks can hydrate
  // without opening cross-origin development resources broadly.
  allowedDevOrigins: ["127.0.0.1", "localhost"],
};

export default nextConfig;
