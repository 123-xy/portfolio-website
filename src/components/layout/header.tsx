"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Coffee, Menu as MenuIcon, Moon, ShoppingBag, Sun, X } from "lucide-react";
import { useTheme } from "next-themes";
import { useCart } from "@/store/cart";
import { cn } from "@/lib/utils";
import { CartDrawer } from "./cart-drawer";

const links = [
  { href: "/", label: "Home" },
  { href: "/menu", label: "Menu" },
  { href: "/about", label: "About" },
  { href: "/gallery", label: "Gallery" },
  { href: "/blog", label: "Blog" },
  { href: "/reservation", label: "Reserve" },
  { href: "/contact", label: "Contact" },
];

export function Header() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();
  const count = useCart((s) => s.items.reduce((n, i) => n + i.quantity, 0));

  useEffect(() => setMounted(true), []);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header
        className={cn(
          "fixed inset-x-0 top-0 z-40 transition-all duration-300",
          scrolled
            ? "border-b border-cream/10 bg-espresso/85 backdrop-blur-xl"
            : "bg-transparent"
        )}
      >
        <nav className="container flex h-18 items-center justify-between py-3">
          <Link href="/" className="flex items-center gap-2 text-cream">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gold-gradient text-espresso">
              <Coffee className="h-5 w-5" />
            </span>
            <span className="font-serif text-xl font-bold tracking-tight">
              Premium<span className="text-gold">Café</span>
            </span>
          </Link>

          <ul className="hidden items-center gap-1 lg:flex">
            {links.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={cn(
                    "relative rounded-full px-4 py-2 text-sm font-medium transition-colors",
                    pathname === link.href
                      ? "text-gold"
                      : "text-cream/80 hover:text-cream"
                  )}
                >
                  {link.label}
                  {pathname === link.href && (
                    <motion.span
                      layoutId="nav-active"
                      className="absolute inset-0 -z-10 rounded-full bg-gold/10"
                    />
                  )}
                </Link>
              </li>
            ))}
          </ul>

          <div className="flex items-center gap-1.5">
            <button
              aria-label="Toggle theme"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="rounded-full p-2.5 text-cream/80 transition-colors hover:bg-cream/10 hover:text-cream"
            >
              {mounted && theme === "dark" ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </button>

            <button
              aria-label="Open cart"
              onClick={() => setCartOpen(true)}
              className="relative rounded-full p-2.5 text-cream/80 transition-colors hover:bg-cream/10 hover:text-cream"
            >
              <ShoppingBag className="h-5 w-5" />
              {mounted && count > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-gold px-1 text-[11px] font-bold text-espresso">
                  {count}
                </span>
              )}
            </button>

            <button
              aria-label="Open menu"
              onClick={() => setMobileOpen(true)}
              className="rounded-full p-2.5 text-cream/80 transition-colors hover:bg-cream/10 hover:text-cream lg:hidden"
            >
              <MenuIcon className="h-5 w-5" />
            </button>
          </div>
        </nav>
      </header>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-espresso lg:hidden"
          >
            <div className="container flex h-18 items-center justify-between py-3">
              <span className="font-serif text-xl font-bold text-cream">
                Premium<span className="text-gold">Café</span>
              </span>
              <button
                aria-label="Close menu"
                onClick={() => setMobileOpen(false)}
                className="rounded-full p-2.5 text-cream/80 hover:bg-cream/10"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <ul className="container mt-8 flex flex-col gap-2">
              {links.map((link, i) => (
                <motion.li
                  key={link.href}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    href={link.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "block rounded-2xl px-5 py-4 font-serif text-2xl transition-colors",
                      pathname === link.href
                        ? "bg-gold/10 text-gold"
                        : "text-cream/80 hover:bg-cream/5"
                    )}
                  >
                    {link.label}
                  </Link>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>

      <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
    </>
  );
}
