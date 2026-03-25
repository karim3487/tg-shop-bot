import type { Metadata } from "next";
import { Providers } from "./_providers/Providers";
import "./globals.css";
import Script from 'next/script';

export const metadata: Metadata = {
  title: "Shop",
  description: "Telegram Mini App Shop",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
      </head>
      <body>
        <Providers>{children}</Providers>
        {process.env.NODE_ENV === "development" && (
          <Script
             src="https://cdn.jsdelivr.net/npm/eruda"
             strategy="afterInteractive"
             onLoad={() => {
               // @ts-ignore
               eruda.init();
             }}
          />
        )}
      </body>
    </html>
  );
}
