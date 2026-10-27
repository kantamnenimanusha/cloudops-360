import { useState } from "react";
import { Badge, Page, Section, Sparkline, Stat, Table, useApi } from "./components";
import { formatBytes, formatDuration, formatPercent, timeAgo } from "./utils";

const when = (v: any) => timeAgo(v);

export function Overview() {
  const s = useApi("/overview");
  const d = s.data || {};
  return (
    <Page title="Overview" state={s}>
      <div className="grid">
        <Section title="Services (Prometheus up)" result={d.services}>
          {(rows) => <Table columns={[{ key: "name", label: "Service" }, { key: "up", label: "State", render: (r) => <Badge value={r.up ? "up" : "down"} /> }]} rows={rows} />}
        </Section>
        <Section title="Cluster nodes" result={d.nodes}>
          {(n) => <Stat label="nodes ready" value={`${n.ready} / ${n.total}`} />}
        </Section>
        <Section title="Node CPU" result={d.cpu}>{(x) => <Stat label="average utilisation" value={formatPercent(x.percent)} />}</Section>
        <Section title="Node memory" result={d.memory}>{(x) => <Stat label="utilisation" value={formatPercent(x.percent)} />}</Section>
        <Section title="Active alerts" result={d.alerts}>
          {(rows) => <Table empty="No active alerts" columns={[{ key: "name", label: "Alert" }, { key: "service", label: "Service" }, { key: "severity", label: "Severity", render: (r) => <Badge value={r.severity} /> }]} rows={rows} />}
        </Section>
        <Section title="Recent pipelines (Jenkins)" result={d.pipelines}>
          {(rows) => <Table columns={[{ key: "job", label: "Job" }, { key: "number", label: "#" }, { key: "result", label: "Result", render: (r) => <Badge value={r.result} /> }, { key: "timestamp", label: "When", render: (r) => when(r.timestamp) }]} rows={rows} />}
        </Section>
        <Section title="Recent deployments (Argo CD)" result={d.deployments}>
          {(rows) => <Table columns={[{ key: "app", label: "App" }, { key: "revision", label: "Git revision", render: (r) => String(r.revision || "").slice(0, 8) }, { key: "deployed_at", label: "When", render: (r) => when(r.deployed_at) }, { key: "health", label: "Health", render: (r) => <Badge value={r.health} /> }]} rows={rows} />}
        </Section>
      </div>
    </Page>
  );
}

export function Infrastructure() {
  const s = useApi("/infrastructure");
  const d = s.data || {};
  return (
    <Page title="Infrastructure" state={s}>
      <div className="grid">
        <Section title="Kubernetes nodes" result={d.nodes}>
          {(rows) => <Table columns={[{ key: "name", label: "Node" }, { key: "ready", label: "Ready", render: (r) => <Badge value={r.ready} /> }, { key: "kubelet_version", label: "Kubelet" }, { key: "cpu", label: "CPU" }, { key: "memory", label: "Memory" }]} rows={rows} />}
        </Section>
        <Section title="Node utilisation (node-exporter)" result={d.node_utilization}>
          {(rows) => <Table columns={[{ key: "instance", label: "Instance" }, { key: "cpu_percent", label: "CPU %" }, { key: "memory_percent", label: "Memory %" }]} rows={rows} />}
        </Section>
        <Section title="AWS EC2 instances" result={d.ec2}>
          {(rows) => <Table empty="No instances in this region" columns={[{ key: "name", label: "Name" }, { key: "id", label: "ID" }, { key: "type", label: "Type" }, { key: "state", label: "State", render: (r) => <Badge value={r.state} /> }, { key: "az", label: "AZ" }]} rows={rows} />}
        </Section>
        <Section title="AWS ECR repositories" result={d.ecr}>
          {(rows) => <Table columns={[{ key: "name", label: "Repository" }, { key: "image_count", label: "Images" }, { key: "immutable", label: "Immutable tags", render: (r) => String(r.immutable) }, { key: "latest_tags", label: "Latest tag", render: (r) => (r.latest_tags || []).join(", ") }]} rows={rows} />}
        </Section>
        <Section title="CloudWatch: EC2 CPU (last hour)" result={d.cloudwatch_ec2_cpu}>
          {(rows) => rows.map((r: any) => <div key={r.instance}><span className="small">{r.instance}</span> <Sparkline points={r.points.map((p: any) => [Date.parse(p[0]), p[1]])} /></div>)}
        </Section>
      </div>
    </Page>
  );
}

export function Kubernetes() {
  const [ns, setNs] = useState("cloudops");
  const s = useApi(`/kubernetes?namespace=${encodeURIComponent(ns)}`);
  const d = s.data || {};
  return (
    <Page title="Kubernetes" state={s}>
      <label>Namespace{" "}
        <select value={ns} onChange={(e) => setNs(e.target.value)}>
          {((d.namespaces && d.namespaces.data) || [ns]).map((n: string) => <option key={n}>{n}</option>)}
        </select>
      </label>
      <Section title="Deployments" result={d.deployments}>
        {(rows) => <Table columns={[{ key: "name", label: "Deployment" }, { key: "ready", label: "Ready", render: (r) => `${r.ready}/${r.desired}` }, { key: "unavailable", label: "Unavailable" }, { key: "images", label: "Image", render: (r) => r.images.join(", ") }]} rows={rows} />}
      </Section>
      <Section title="Pods" result={d.pods}>
        {(rows) => <Table columns={[{ key: "name", label: "Pod" }, { key: "phase", label: "Phase", render: (r) => <Badge value={r.phase} /> }, { key: "ready", label: "Ready", render: (r) => <Badge value={r.ready} /> }, { key: "restarts", label: "Restarts" }, { key: "state", label: "State", render: (r) => r.containers.map((c: any) => c.state).join(", ") }, { key: "node", label: "Node" }]} rows={rows} />}
      </Section>
      <Section title="Resource usage (cAdvisor via Prometheus)" result={d.usage}>
        {(rows) => <Table columns={[{ key: "pod", label: "Pod" }, { key: "cpu_cores", label: "CPU (cores)" }, { key: "memory_bytes", label: "Memory", render: (r) => formatBytes(r.memory_bytes) }]} rows={rows} />}
      </Section>
    </Page>
  );
}

export function CICD() {
  const s = useApi("/cicd");
  const jobs = s.data?.jobs;
  return (
    <Page title="CI/CD (Jenkins)" state={s}>
      <Section title="Pipelines" result={jobs}>
        {(rows) => (
          <>
            <Table columns={[{ key: "job", label: "Job" }, { key: "success", label: "Succeeded" }, { key: "failed", label: "Failed" }, { key: "avg_duration_ms", label: "Avg duration", render: (r) => formatDuration(r.avg_duration_ms) }, { key: "latest_image", label: "Latest image" }, { key: "error", label: "Note", render: (r) => r.error || "" }]} rows={rows} />
            {rows.map((j: any) => (
              <details key={j.job}><summary>{j.job}: recent builds</summary>
                <Table empty="No builds yet" columns={[{ key: "number", label: "#" }, { key: "result", label: "Result", render: (r) => <Badge value={r.result} /> }, { key: "timestamp", label: "When", render: (r) => when(r.timestamp) }, { key: "duration_ms", label: "Duration", render: (r) => formatDuration(r.duration_ms) }, { key: "description", label: "Image" }]} rows={j.builds} />
              </details>
            ))}
          </>
        )}
      </Section>
    </Page>
  );
}

function Counts({ counts }: { counts: Record<string, number> }) {
  return <>{Object.entries(counts).map(([k, v]) => <span key={k} className="chip">{k}: {v}</span>)}</>;
}

export function Security() {
  const s = useApi("/security", 30000);
  const d = s.data || {};
  return (
    <Page title="Security (Trivy)" state={s}>
      <p className="muted">Gate policy: fail on {d.gate_severity || "…"} or worse. Jenkins is the source of truth for the actual gate.</p>
      <Section title="Latest scan per pipeline" result={d.reports}>
        {(rows) => rows.map((r: any) => (
          <div key={r.job} className="subcard">
            <h4>{r.job}</h4>
            {["fs", "image"].map((k) => r[k] ? (
              <div key={k}>
                <strong>{k === "fs" ? "Dependencies" : "Container image"}</strong>{" "}
                <Badge value={r[k].gate.passed ? "passed" : "failed"} /> <Counts counts={r[k].counts} />
                <Table empty="No findings" columns={[{ key: "id", label: "CVE" }, { key: "severity", label: "Severity", render: (f) => <Badge value={f.severity} /> }, { key: "package", label: "Package" }, { key: "installed", label: "Installed" }, { key: "fixed", label: "Fixed in" }]} rows={r[k].findings.slice(0, 8)} />
              </div>
            ) : <p key={k} className="muted">{k === "fs" ? "Dependencies" : "Image"}: no report archived yet</p>)}
          </div>
        ))}
      </Section>
    </Page>
  );
}

export function Monitoring() {
  const s = useApi("/monitoring");
  const d = s.data || {};
  const series = (r: any) => (r?.data || []).map((x: any) => <div key={x.service}><span className="small">{x.service}</span> <Sparkline points={x.points} /></div>);
  return (
    <Page title="Monitoring (Prometheus)" state={s}>
      <div className="grid">
        <Section title="Request rate (req/s)" result={d.request_rate}>{(rows) => <Table columns={[{ key: "service", label: "Service" }, { key: "value", label: "req/s", render: (r) => r.value.toFixed(2) }]} rows={rows} />}</Section>
        <Section title="Error ratio (5xx)" result={d.error_ratio}>{(rows) => <Table empty="No traffic" columns={[{ key: "service", label: "Service" }, { key: "value", label: "5xx", render: (r) => formatPercent(r.value * 100) }]} rows={rows} />}</Section>
        <Section title="Latency p95" result={d.latency_p95_seconds}>{(rows) => <Table empty="No traffic" columns={[{ key: "service", label: "Service" }, { key: "value", label: "p95", render: (r) => `${(r.value * 1000).toFixed(0)} ms` }]} rows={rows} />}</Section>
        <Section title="Availability (1h)" result={d.availability_1h}>{(rows) => <Table columns={[{ key: "service", label: "Service" }, { key: "value", label: "Up", render: (r) => formatPercent(r.value * 100) }]} rows={rows} />}</Section>
        <Section title="Request rate trend" result={d.request_rate_series}>{() => series(d.request_rate_series)}</Section>
        <Section title="Latency p95 trend" result={d.latency_p95_series}>{() => series(d.latency_p95_series)}</Section>
      </div>
    </Page>
  );
}

export function Logs() {
  const [service, setService] = useState("");
  const [level, setLevel] = useState("");
  const [q, setQ] = useState("");
  const params = new URLSearchParams();
  if (service) params.set("service", service);
  if (level) params.set("level", level);
  if (q) params.set("q", q);
  const s = useApi(`/logs?${params.toString()}`, 10000);
  return (
    <Page title="Logs (Loki)" state={s}>
      <div className="filters">
        <select value={service} onChange={(e) => setService(e.target.value)}>
          <option value="">all services</option>
          {["orders-service", "inventory-service", "cloudops-backend"].map((x) => <option key={x}>{x}</option>)}
        </select>
        <select value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="">any level</option><option>ERROR</option><option>WARN</option><option>INFO</option>
        </select>
        <input placeholder="contains text" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <Section title="Log lines" result={s.data}>
        {(data) => (
          <>
            <code className="small">{data.query}</code>
            <Table empty="No log lines in the last 30 minutes" columns={[{ key: "ts", label: "Time", render: (r) => new Date(r.ts).toLocaleTimeString() }, { key: "service", label: "Service" }, { key: "level", label: "Level", render: (r) => <Badge value={r.level || "-"} /> }, { key: "line", label: "Message", render: (r) => <span className="mono">{r.line}</span> }]} rows={data.lines} />
          </>
        )}
      </Section>
    </Page>
  );
}

export function Alerts() {
  const s = useApi("/alerts", 10000);
  const d = s.data || {};
  return (
    <Page title="Alerts (Alertmanager)" state={s}>
      <Section title="Active alerts" result={d.active}>
        {(rows) => <Table empty="No active alerts" columns={[{ key: "name", label: "Alert" }, { key: "severity", label: "Severity", render: (r) => <Badge value={r.severity} /> }, { key: "service", label: "Service" }, { key: "summary", label: "Summary" }, { key: "starts_at", label: "Since", render: (r) => when(r.starts_at) }]} rows={rows} />}
      </Section>
      <Section title="History (webhook receiver, in memory)" result={d.history}>
        {(rows) => <Table empty="No alert events received since backend start" columns={[{ key: "name", label: "Alert" }, { key: "status", label: "Event", render: (r) => <Badge value={r.status} /> }, { key: "severity", label: "Severity" }, { key: "service", label: "Service" }, { key: "starts_at", label: "Started", render: (r) => when(r.starts_at) }]} rows={rows} />}
      </Section>
    </Page>
  );
}

export function Deployments() {
  const s = useApi("/deployments");
  return (
    <Page title="Deployments (Argo CD)" state={s}>
      <Section title="Applications" result={s.data?.applications}>
        {(rows) => (
          <>
            <Table columns={[{ key: "name", label: "Application" }, { key: "sync", label: "Sync", render: (r) => <Badge value={r.sync} /> }, { key: "health", label: "Health", render: (r) => <Badge value={r.health} /> }, { key: "revision", label: "Revision", render: (r) => String(r.revision || "").slice(0, 8) }, { key: "images", label: "Images", render: (r) => (r.images || []).join(", ") }, { key: "redeployed_previous_revision", label: "Previous revision re-deployed", render: (r) => (r.redeployed_previous_revision ? "yes" : "no") }]} rows={rows} />
            {rows.map((a: any) => (
              <details key={a.name}><summary>{a.name}: deployment history</summary>
                <Table empty="No history yet" columns={[{ key: "id", label: "ID" }, { key: "revision", label: "Git revision", render: (r) => String(r.revision || "").slice(0, 8) }, { key: "deployed_at", label: "Deployed", render: (r) => when(r.deployed_at) }]} rows={a.history} />
              </details>
            ))}
          </>
        )}
      </Section>
    </Page>
  );
}
