package com.cloudops360.orders;

import org.springframework.stereotype.Component;

/** Mutable demo state. Only modifiable through {@link ChaosController}, which is disabled by default. */
@Component
public class ChaosState {
    private volatile double errorRate = 0.0;
    private volatile long latencyMs = 0;
    private volatile boolean ready = true;

    public double errorRate() { return errorRate; }
    public long latencyMs() { return latencyMs; }
    public boolean ready() { return ready; }

    public void errorRate(double v) { this.errorRate = Math.min(Math.max(v, 0.0), 1.0); }
    public void latencyMs(long v) { this.latencyMs = Math.min(Math.max(v, 0), 10_000); }
    public void ready(boolean v) { this.ready = v; }

    public void reset() {
        errorRate = 0.0;
        latencyMs = 0;
        ready = true;
    }
}
