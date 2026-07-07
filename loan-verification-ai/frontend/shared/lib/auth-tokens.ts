/**
 * Browser-side token storage for the auth session.
 *
 * Tokens live in localStorage keyed under a single namespace. This is a
 * deliberate, documented trade-off: it keeps the SPA simple and works with the
 * client-rendered app shell. A future hardening step (Phase 7+ / production)
 * can move refresh tokens to httpOnly cookies to defend against XSS token
 * theft; the access-token flow here is otherwise unchanged.
 */

const ACCESS_KEY = "verifyco.access_token";
const REFRESH_KEY = "verifyco.refresh_token";

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

const isBrowser = typeof window !== "undefined";

export function getAccessToken(): string | null {
  return isBrowser ? window.localStorage.getItem(ACCESS_KEY) : null;
}

export function getRefreshToken(): string | null {
  return isBrowser ? window.localStorage.getItem(REFRESH_KEY) : null;
}

export function setTokens(pair: TokenPair): void {
  if (!isBrowser) return;
  window.localStorage.setItem(ACCESS_KEY, pair.accessToken);
  window.localStorage.setItem(REFRESH_KEY, pair.refreshToken);
}

export function clearTokens(): void {
  if (!isBrowser) return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}
