package com.cloudops360.orders;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

/** Part of the READINESS group only: lets a demo make the pod "not ready" while liveness stays UP. */
@Component("chaos")
public class ChaosHealthIndicator implements HealthIndicator {
    private final ChaosState state;

    public ChaosHealthIndicator(ChaosState state) {
        this.state = state;
    }

    @Override
    public Health health() {
        return state.ready() ? Health.up().build() : Health.down().withDetail("reason", "readiness disabled via chaos endpoint (demo)").build();
    }
}
