import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge conditional class names and resolve Tailwind conflicts
 * (last-writer-wins on conflicting utilities).
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
