export function formatDuration(ms?: number | null): string {
  if (ms == null) return "-";
  if (ms < 1000) return `${ms} ms`;
  const s = Math.round(ms / 1000);
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${s % 60}s`;
}

export function formatBytes(b?: number | null): string {
  if (b == null) return "-";
  const units = ["B", "KiB", "MiB", "GiB", "TiB"];
  let i = 0;
  let v = b;
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
  return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export function formatPercent(v?: number | null, digits = 1): string {
  return v == null || Number.isNaN(v) ? "-" : `${v.toFixed(digits)}%`;
}

export function timeAgo(value?: string | number | null, now: number = Date.now()): string {
  if (value == null || value === "") return "-";
  const t = typeof value === "number" ? value : Date.parse(value);
  if (Number.isNaN(t)) return "-";
  const s = Math.max(0, Math.round((now - t) / 1000));
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

export function badgeClass(status?: string | null): string {
  const s = (status || "").toLowerCase();
  if (["ok", "success", "healthy", "synced", "running", "up", "true", "passed", "resolved", "ready"].includes(s)) return "good";
  if (["failure", "failed", "degraded", "outofsync", "critical", "unavailable", "down", "false", "firing", "error"].includes(s)) return "bad";
  if (["warning", "progressing", "unstable", "pending", "high", "unknown", "aborted"].includes(s)) return "warn";
  return "neutral";
}
