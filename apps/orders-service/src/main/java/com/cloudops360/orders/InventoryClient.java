package com.cloudops360.orders;

import java.util.Map;

import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

public class InventoryClient {

    public record ReserveResult(String sku, int reserved, int remaining) {
    }

    private final RestClient restClient;

    public InventoryClient(RestClient restClient) {
        this.restClient = restClient;
    }

    public ReserveResult reserve(String sku, int quantity) {
        try {
            return restClient.post()
                    .uri("/items/{sku}/reserve", sku)
                    .body(Map.of("quantity", quantity))
                    .retrieve()
                    .body(ReserveResult.class);
        } catch (HttpClientErrorException e) {
            if (e.getStatusCode().value() == 404) {
                throw new InventoryException(InventoryException.Kind.UNKNOWN_SKU, "unknown sku " + sku);
            }
            if (e.getStatusCode().value() == 409) {
                throw new InventoryException(InventoryException.Kind.INSUFFICIENT_STOCK, "insufficient stock for " + sku);
            }
            throw new InventoryException(InventoryException.Kind.UNAVAILABLE, "inventory rejected request: " + e.getStatusCode());
        } catch (RestClientException e) {
            throw new InventoryException(InventoryException.Kind.UNAVAILABLE, "inventory-service unavailable");
        }
    }
}
