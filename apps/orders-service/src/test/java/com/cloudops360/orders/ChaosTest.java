package com.cloudops360.orders;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = {"chaos.enabled=true", "chaos.token=test-token"})
@AutoConfigureMockMvc
class ChaosTest {
    @Autowired MockMvc mvc;
    @Autowired ChaosState state;

    @AfterEach
    void reset() {
        state.reset();
    }

    @Test
    void requiresToken() throws Exception {
        mvc.perform(get("/chaos/state")).andExpect(status().isUnauthorized());
        mvc.perform(get("/chaos/state").header("X-Chaos-Token", "wrong")).andExpect(status().isUnauthorized());
        mvc.perform(get("/chaos/state").header("X-Chaos-Token", "test-token")).andExpect(status().isOk());
    }

    @Test
    void injectedErrorsAffectOrdersApi() throws Exception {
        mvc.perform(post("/chaos/errors?rate=1").header("X-Chaos-Token", "test-token")).andExpect(status().isOk());
        mvc.perform(get("/api/orders")).andExpect(status().isInternalServerError());
        mvc.perform(post("/chaos/reset").header("X-Chaos-Token", "test-token")).andExpect(status().isOk());
        mvc.perform(get("/api/orders")).andExpect(status().isOk());
    }

    @Test
    void latencyIsClampedAndApplied() throws Exception {
        mvc.perform(post("/chaos/latency?ms=20").header("X-Chaos-Token", "test-token")).andExpect(jsonPath("$.latencyMs").value(20));
        mvc.perform(get("/api/orders")).andExpect(status().isOk());
    }

    @Test
    void readinessGoesDownButLivenessStaysUp() throws Exception {
        mvc.perform(post("/chaos/ready?value=false").header("X-Chaos-Token", "test-token")).andExpect(status().isOk());
        mvc.perform(get("/actuator/health/readiness")).andExpect(status().isServiceUnavailable());
        mvc.perform(get("/actuator/health/liveness")).andExpect(status().isOk());
    }
}
