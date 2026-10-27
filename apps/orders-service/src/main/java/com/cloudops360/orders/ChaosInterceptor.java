package com.cloudops360.orders;

import java.util.concurrent.ThreadLocalRandom;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/** Applies the simulated latency/error state to /api/** requests (after handler mapping, so metrics keep the real uri label). */
@Component
public class ChaosInterceptor implements HandlerInterceptor {
    private final ChaosState state;

    public ChaosInterceptor(ChaosState state) {
        this.state = state;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        if (state.latencyMs() > 0) {
            Thread.sleep(state.latencyMs());
        }
        if (state.errorRate() > 0 && ThreadLocalRandom.current().nextDouble() < state.errorRate()) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("application/json");
            response.getWriter().write("{\"error\":\"chaos: injected error\"}");
            return false;
        }
        return true;
    }
}
