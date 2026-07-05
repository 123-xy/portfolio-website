"use client";

import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      {children}
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: "#3a2318",
            border: "1px solid rgba(201,162,75,0.3)",
            color: "#f6efe6",
          },
        }}
      />
    </ThemeProvider>
  );
}
