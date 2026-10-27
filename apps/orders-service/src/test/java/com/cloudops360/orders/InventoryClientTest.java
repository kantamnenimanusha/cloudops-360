package com.cloudops360.orders;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

class InventoryClientTest {
    private MockRestServiceServer server;
    private InventoryClient client;

    @BeforeEach
    void setUp() {
        RestClient.Builder builder = RestClient.builder().baseUrl("http://inventory.test");
        server = MockRestServiceServer.bindTo(builder).build();
        client = new InventoryClient(builder.build());
    }

    @Test
    void reservesStock() {
        server.expect(requestTo("http://inventory.test/items/SKU-1/reserve")).andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess("{\"sku\":\"SKU-1\",\"reserved\":2,\"remaining\":8}", MediaType.APPLICATION_JSON));
        assertEquals(8, client.reserve("SKU-1", 2).remaining());
        server.verify();
    }

    @Test
    void mapsStatusCodes() {
        server.expect(requestTo("http://inventory.test/items/A/reserve")).andRespond(withStatus(HttpStatus.NOT_FOUND));
        server.expect(requestTo("http://inventory.test/items/B/reserve")).andRespond(withStatus(HttpStatus.CONFLICT));
        server.expect(requestTo("http://inventory.test/items/C/reserve")).andRespond(withStatus(HttpStatus.BAD_REQUEST));
        server.expect(requestTo("http://inventory.test/items/D/reserve")).andRespond(withStatus(HttpStatus.INTERNAL_SERVER_ERROR));
        assertEquals(InventoryException.Kind.UNKNOWN_SKU, assertThrows(InventoryException.class, () -> client.reserve("A", 1)).kind());
        assertEquals(InventoryException.Kind.INSUFFICIENT_STOCK, assertThrows(InventoryException.class, () -> client.reserve("B", 1)).kind());
        assertEquals(InventoryException.Kind.UNAVAILABLE, assertThrows(InventoryException.class, () -> client.reserve("C", 1)).kind());
        assertEquals(InventoryException.Kind.UNAVAILABLE, assertThrows(InventoryException.class, () -> client.reserve("D", 1)).kind());
    }
}
