/**
 * api.ts – Centralised authenticated fetch wrapper with automatic token refresh.
 *
 * Usage:
 *   import { apiFetch } from "@/lib/api";
 *
 *   const res = await apiFetch("/audits");          // GET by default
 *   const data = await res.json();
 *
 * On a 401, the wrapper will:
 *   1. Attempt a silent refresh via POST /auth/refresh.
 *   2. Retry all queued requests with the new token.
 *   3. If refresh fails, clear auth state and redirect to /login.
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://empathai-backend-production-a6c7.up.railway.app";

// ----- Refresh state (module-level singletons) -----
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token as string);
    }
  });
  failedQueue = [];
}

// ----- Token helpers -----
function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("ay11sutra_token");
}

function setToken(token: string): void {
  localStorage.setItem("ay11sutra_token", token);
}

function clearAuth(): void {
  localStorage.removeItem("ay11sutra_token");
  localStorage.removeItem("ay11sutra_auth");
  localStorage.removeItem("ay11sutra_user");
}

// ----- Silent refresh -----
async function refreshToken(): Promise<string> {
  const expiredToken = getToken();
  if (!expiredToken) throw new Error("No token to refresh");

  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${expiredToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Token refresh failed");
  }

  const data = await res.json();
  const newToken: string = data.access_token;
  setToken(newToken);

  // Update cached user info if present
  if (data.user) {
    localStorage.setItem("ay11sutra_user", JSON.stringify(data.user));
  }

  return newToken;
}

// ----- Main wrapper -----
export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const requestOptions: RequestInit = { ...options, headers };

  let response = await fetch(`${API_BASE}${path}`, requestOptions);

  // Not a 401 – return as-is
  if (response.status !== 401) {
    return response;
  }

  // ---- 401 handling ----

  // If another refresh is in flight, queue this request
  if (isRefreshing) {
    return new Promise<Response>((resolve, reject) => {
      failedQueue.push({
        resolve: async (newToken: string) => {
          const retryHeaders = {
            ...headers,
            Authorization: `Bearer ${newToken}`,
          };
          resolve(await fetch(`${API_BASE}${path}`, { ...requestOptions, headers: retryHeaders }));
        },
        reject,
      });
    });
  }

  // This request kicks off the refresh
  isRefreshing = true;

  try {
    const newToken = await refreshToken();
    processQueue(null, newToken);

    // Retry the original request with the new token
    const retryHeaders = { ...headers, Authorization: `Bearer ${newToken}` };
    response = await fetch(`${API_BASE}${path}`, {
      ...requestOptions,
      headers: retryHeaders,
    });

    return response;
  } catch (err) {
    processQueue(err, null);

    // Refresh failed – clear auth and redirect to login
    clearAuth();
    if (typeof window !== "undefined") {
      window.location.href = "/login?reason=session_expired";
    }
    // Return a synthetic 401 so callers don't throw
    return new Response(JSON.stringify({ detail: "Session expired" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  } finally {
    isRefreshing = false;
  }
}

/** Convenience: apiFetch but returns parsed JSON directly, throws on non-ok */
export async function apiFetchJson<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await apiFetch(path, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail || `Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}
