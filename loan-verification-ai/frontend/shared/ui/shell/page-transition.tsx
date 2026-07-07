"use client";

import * as React from "react";
import { motion } from "framer-motion";

/**
 * Subtle fade/slide on mount, mimicking a native screen push. Kept short
 * (180ms) so navigation still feels instant.
 */
export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      className="flex flex-1 flex-col"
    >
      {children}
    </motion.div>
  );
}
