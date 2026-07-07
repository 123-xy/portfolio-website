import { env } from "@/shared/lib/env";

/**
 * Thin, typed fetch wrapper around the backend REST API (/api/v1).
 *
 * Responsibilities kept deliberately narrow:
 *  - attach the bearer access token,
 *  - serialize/deserialize JSON,
 *  - normalize errors into a single ApiError shape,
 *  - transparently refresh the access token once on a 401 and retry.
 *
 * Token *storage* is injected (getAccessToken / refresh) so this module has no
 * hard dependency on where tokens live — the auth feature wires that up in a
 * later phase. For Phase 5 the defaults are no-ops, so the client is usable
 * against public endpoints and fully unit-testable.
 */

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type TokenProvider = () => string | null | Promise<string | null>;
type TokenRefresher = () => Promise<string | null>;

interface ApiClientOptions {
  baseUrl?: string;
  getAccessToken?: TokenProvider;
  refreshAccessToken?: TokenRefresher;
}

export interface RequestOptions extends Omit<RequestInit, "body"> {
  /** JSON-serializable body; set automatically with the correct content-type. */
  json?: unknown;
  /** Skip the Authorization header (e.g. for login/register). */
  skipAuth?: boolean;
}

export class ApiClient {
  private readonly baseUrl: string;
  private readonly getAccessToken: TokenProvider;
  private readonly refreshAccessToken: TokenRefresher;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? env.NEXT_PUBLIC_API_BASE_URL).replace(/\/$/, "");
    this.getAccessToken = options.getAccessToken ?? (() => null);
    this.refreshAccessToken = options.refreshAccessToken ?? (async () => null);
  }

  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const response = await this.send(path, options);

    // One transparent refresh-and-retry on an expired access token.
    if (response.status === 401 && !options.skipAuth) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        const retry = await this.send(path, options, refreshed);
        return this.parse<T>(retry);
      }
    }

    return this.parse<T>(response);
  }

  get<T>(path: string, options?: RequestOptions) {
    return this.request<T>(path, { ...options, method: "GET" });
  }
  post<T>(path: string, json?: unknown, options?: RequestOptions) {
    return this.request<T>(path, { ...options, method: "POST", json });
  }
  patch<T>(path: string, json?: unknown, options?: RequestOptions) {
    return this.request<T>(path, { ...options, method: "PATCH", json });
  }
  delete<T>(path: string, options?: RequestOptions) {
    return this.request<T>(path, { ...options, method: "DELETE" });
  }

  private async send(
    path: string,
    options: RequestOptions,
    overrideToken?: string,
  ): Promise<Response> {
    const { json, skipAuth, headers, ...rest } = options;
    const finalHeaders = new Headers(headers);

    if (json !== undefined) {
      finalHeaders.set("Content-Type", "application/json");
    }
    if (!skipAuth) {
      const token = overrideToken ?? (await this.getAccessToken());
      if (token) finalHeaders.set("Authorization", `Bearer ${token}`);
    }

    return fetch(`${this.baseUrl}${path}`, {
      ...rest,
      headers: finalHeaders,
      body: json !== undefined ? JSON.stringify(json) : undefined,
    });
  }

  private async parse<T>(response: Response): Promise<T> {
    if (response.status === 204) {
      return undefined as T;
    }

    const contentType = response.headers.get("content-type") ?? "";
    const isJson = contentType.includes("application/json");
    const payload = isJson ? await response.json().catch(() => null) : await response.text();

    if (!response.ok) {
      const message =
        (isJson && payload && typeof payload === "object" && "detail" in payload
          ? String((payload as { detail: unknown }).detail)
          : null) ?? `Request failed with status ${response.status}`;
      throw new ApiError(response.status, message, payload);
    }

    return payload as T;
  }
}

/** Default browser client instance. Token wiring is attached by the auth feature. */
export const apiClient = new ApiClient();
