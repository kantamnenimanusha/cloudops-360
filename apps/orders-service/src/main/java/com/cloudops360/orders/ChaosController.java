package com.cloudops360.orders;

import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * DEMO ONLY. Disabled (404) unless chaos.enabled=true and a chaos.token is configured.
 * The failures are simulated; how Kubernetes/Prometheus react to them is real.
 */
@RestController
@RequestMapping("/chaos")
public class ChaosController {
    private final ChaosState state;
    private final boolean enabled;
    private final String token;

    public ChaosController(ChaosState state, @Value("${chaos.enabled:false}") boolean enabled, @Value("${chaos.token:}") String token) {
        this.state = state;
        this.enabled = enabled;
        this.token = token;
    }

    private void guard(String provided) {
        if (!enabled || token.isBlank()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        }
        boolean same = provided != null && MessageDigest.isEqual(provided.getBytes(StandardCharsets.UTF_8), token.getBytes(StandardCharsets.UTF_8));
        if (!same) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "invalid chaos token");
        }
    }

    private Map<String, Object> snapshot() {
        return Map.of("errorRate", state.errorRate(), "latencyMs", state.latencyMs(), "ready", state.ready());
    }

    @GetMapping("/state")
    public Map<String, Object> get(@RequestHeader(value = "X-Chaos-Token", required = false) String t) {
        guard(t);
        return snapshot();
    }

    @PostMapping("/errors")
    public Map<String, Object> errors(@RequestParam double rate, @RequestHeader(value = "X-Chaos-Token", required = false) String t) {
        guard(t);
        state.errorRate(rate);
        return snapshot();
    }

    @PostMapping("/latency")
    public Map<String, Object> latency(@RequestParam long ms, @RequestHeader(value = "X-Chaos-Token", required = false) String t) {
        guard(t);
        state.latencyMs(ms);
        return snapshot();
    }

    @PostMapping("/ready")
    public Map<String, Object> ready(@RequestParam boolean value, @RequestHeader(value = "X-Chaos-Token", required = false) String t) {
        guard(t);
        state.ready(value);
        return snapshot();
    }

    @PostMapping("/reset")
    public Map<String, Object> reset(@RequestHeader(value = "X-Chaos-Token", required = false) String t) {
        guard(t);
        state.reset();
        return snapshot();
    }

    @PostMapping("/crash")
    public Map<String, Object> crash(@RequestHeader(value = "X-Chaos-Token", required = false) String t) {
        guard(t);
        Thread killer = new Thread(() -> {
            try {
                Thread.sleep(500);
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }
            Runtime.getRuntime().halt(1);
        });
        killer.setDaemon(true);
        killer.start();
        return Map.of("crashing", true);
    }
}
