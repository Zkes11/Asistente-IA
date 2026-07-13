import "./globals.css";

import type { ReactNode } from "react";

import { Providers } from "./providers";

export const metadata = {
  title: "OrientaIA",
  description: "Orientacion vocacional exploratoria y explicable",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es-CO">
      <body className="bg-background text-text antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
