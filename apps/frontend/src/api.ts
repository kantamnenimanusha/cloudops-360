const KEY = "cloudops360.token";

export const getToken = (): string | null => sessionStorage.getItem(KEY);
export function setToken(token: string | null) {
  if (token) sessionStorage.setItem(KEY, token);
  else sessionStorage.removeItem(KEY);
}

export async function login(username: string, password: string): Promise<{ role: string }> {
  const r = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (r.status === 429) throw new Error("Too many attempts. Wait a few minutes.");
  if (!r.ok) throw new Error("Invalid credentials");
  const body = await r.json();
  setToken(body.access_token);
  return { role: body.role };
}

export async function apiGet(path: string): Promise<any> {
  const r = await fetch(`/api/v1${path}`, { headers: { Authorization: `Bearer ${getToken()}` } });
  if (r.status === 401) {
    setToken(null);
    window.dispatchEvent(new Event("auth-expired"));
    throw new Error("Session expired");
  }
  if (!r.ok) throw new Error(`Backend returned HTTP ${r.status}`);
  return r.json();
}
