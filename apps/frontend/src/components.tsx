import { useCallback, useEffect, useState } from "react";
import { apiGet } from "./api";
import { badgeClass, timeAgo } from "./utils";

export interface Result<T = any> {
  status: "ok" | "unavailable" | "not_configured";
  source: string;
  fetched_at: string | null;
  error: string | null;
  data: T | null;
}

export function useApi(path: string, intervalMs = 15000) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    try {
      setData(await apiGet(path));
      setError(null);
    } catch (e: any) {
      setError(e.message || "request failed");
    } finally {
      setLoading(false);
    }
  }, [path]);
  useEffect(() => {
    setLoading(true);
    load();
    const t = setInterval(load, intervalMs);
    return () => clearInterval(t);
  }, [load, intervalMs]);
  return { data, error, loading, reload: load };
}

export function Badge({ value }: { value: any }) {
  return <span className={`badge ${badgeClass(String(value))}`}>{String(value)}</span>;
}

/** A panel backed by exactly one data source. It never fabricates data: failures are shown explicitly. */
export function Section({ title, result, children }: { title: string; result?: Result | null; children: (data: any) => any }) {
  return (
    <section className="card">
      <header>
        <h3>{title}</h3>
        {result && <Badge value={result.status} />}
      </header>
      {!result && <p className="muted">Loading…</p>}
      {result && result.status !== "ok" && (
        <p className={result.status === "unavailable" ? "error" : "muted"}>
          {result.status === "unavailable" ? "Source unavailable: " : "Not configured: "}
          {result.error}
        </p>
      )}
      {result && result.status === "ok" && children(result.data)}
      {result && <footer className="muted">source: {result.source}{result.fetched_at ? ` · ${timeAgo(result.fetched_at)}` : ""}</footer>}
    </section>
  );
}

export function Table({ columns, rows, empty = "No data" }: { columns: { key: string; label: string; render?: (row: any) => any }[]; rows: any[]; empty?: string }) {
  if (!rows || rows.length === 0) return <p className="muted">{empty}</p>;
  return (
    <div className="scroll">
      <table>
        <thead><tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>{columns.map((c) => <td key={c.key}>{c.render ? c.render(r) : String(r[c.key] ?? "-")}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Stat({ label, value, sub }: { label: string; value: any; sub?: string }) {
  return (
    <div className="stat">
      <div className="stat-value">{value}</div>
      <div className="muted">{label}</div>
      {sub && <div className="muted small">{sub}</div>}
    </div>
  );
}

export function Sparkline({ points, width = 220, height = 40 }: { points: [number, number][]; width?: number; height?: number }) {
  if (!points || points.length < 2) return <span className="muted small">no data</span>;
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const [x0, x1] = [Math.min(...xs), Math.max(...xs)];
  const [y0, y1] = [Math.min(...ys, 0), Math.max(...ys) || 1];
  const path = points
    .map((p) => `${(((p[0] - x0) / (x1 - x0 || 1)) * width).toFixed(1)},${(height - ((p[1] - y0) / (y1 - y0 || 1)) * height).toFixed(1)}`)
    .join(" ");
  return <svg width={width} height={height}><polyline points={path} fill="none" stroke="currentColor" strokeWidth="2" /></svg>;
}

export function Page({ title, state, children }: { title: string; state: { error: string | null; loading: boolean; reload: () => void }; children: any }) {
  return (
    <div>
      <div className="page-head">
        <h2>{title}</h2>
        <button onClick={state.reload}>Refresh</button>
      </div>
      {state.error && <p className="error">Cannot reach the CloudOps 360 backend: {state.error}</p>}
      {state.loading ? <p className="muted">Loading…</p> : children}
    </div>
  );
}
