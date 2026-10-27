package com.cloudops360.orders;

import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerTest {
    @Autowired MockMvc mvc;
    @MockitoBean InventoryClient inventory;

    private static final String VALID = "{\"sku\":\"SKU-1001\",\"quantity\":2,\"customer\":\"alice\"}";

    @Test
    void createsAndListsAndFetchesOrder() throws Exception {
        when(inventory.reserve("SKU-1001", 2)).thenReturn(new InventoryClient.ReserveResult("SKU-1001", 2, 98));
        String body = mvc.perform(post("/api/orders").contentType(MediaType.APPLICATION_JSON).content(VALID))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("CONFIRMED"))
                .andReturn().getResponse().getContentAsString();
        String id = body.replaceAll(".*\"id\":\"([^\"]+)\".*", "$1");
        mvc.perform(get("/api/orders")).andExpect(status().isOk()).andExpect(jsonPath("$[0].sku").value("SKU-1001"));
        mvc.perform(get("/api/orders/" + id)).andExpect(status().isOk()).andExpect(jsonPath("$.customer").value("alice"));
    }

    @Test
    void rejectsInvalidPayload() throws Exception {
        mvc.perform(post("/api/orders").contentType(MediaType.APPLICATION_JSON).content("{\"sku\":\"\",\"quantity\":0,\"customer\":\"\"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void unknownOrderIs404() throws Exception {
        mvc.perform(get("/api/orders/does-not-exist")).andExpect(status().isNotFound());
    }

    @Test
    void mapsInventoryFailures() throws Exception {
        when(inventory.reserve(anyString(), anyInt()))
                .thenThrow(new InventoryException(InventoryException.Kind.UNKNOWN_SKU, "unknown sku"))
                .thenThrow(new InventoryException(InventoryException.Kind.INSUFFICIENT_STOCK, "insufficient"))
                .thenThrow(new InventoryException(InventoryException.Kind.UNAVAILABLE, "down"));
        mvc.perform(post("/api/orders").contentType(MediaType.APPLICATION_JSON).content(VALID)).andExpect(status().isNotFound());
        mvc.perform(post("/api/orders").contentType(MediaType.APPLICATION_JSON).content(VALID)).andExpect(status().isConflict());
        mvc.perform(post("/api/orders").contentType(MediaType.APPLICATION_JSON).content(VALID)).andExpect(status().isServiceUnavailable());
    }

    @Test
    void versionEndpoint() throws Exception {
        mvc.perform(get("/api/version")).andExpect(status().isOk()).andExpect(jsonPath("$.service").value("orders-service"));
    }

    @Test
    void chaosIsDisabledByDefault() throws Exception {
        mvc.perform(get("/chaos/state")).andExpect(status().isNotFound());
    }

    @Test
    void probesAreUp() throws Exception {
        mvc.perform(get("/actuator/health/liveness")).andExpect(status().isOk());
        mvc.perform(get("/actuator/health/readiness")).andExpect(status().isOk());
    }
}
