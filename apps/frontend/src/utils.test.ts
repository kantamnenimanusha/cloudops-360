import { describe, expect, it } from "vitest";
import { badgeClass, formatBytes, formatDuration, formatPercent, timeAgo } from "./utils";

describe("utils", () => {
  it("formats durations", () => {
    expect(formatDuration(null)).toBe("-");
    expect(formatDuration(500)).toBe("500 ms");
    expect(formatDuration(90_000)).toBe("1m 30s");
  });
  it("formats bytes", () => {
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(1536)).toBe("1.5 KiB");
    expect(formatBytes(undefined)).toBe("-");
  });
  it("formats percent", () => {
    expect(formatPercent(12.345)).toBe("12.3%");
    expect(formatPercent(NaN)).toBe("-");
  });
  it("computes relative time", () => {
    const now = Date.parse("2026-01-01T00:10:00Z");
    expect(timeAgo("2026-01-01T00:05:00Z", now)).toBe("5m ago");
    expect(timeAgo(null, now)).toBe("-");
    expect(timeAgo("garbage", now)).toBe("-");
  });
  it("maps statuses to badge classes", () => {
    expect(badgeClass("Healthy")).toBe("good");
    expect(badgeClass("FAILURE")).toBe("bad");
    expect(badgeClass("Progressing")).toBe("warn");
    expect(badgeClass("whatever")).toBe("neutral");
  });
});
