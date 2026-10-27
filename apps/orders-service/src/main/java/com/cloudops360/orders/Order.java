package com.cloudops360.orders;

import java.time.Instant;

public record Order(String id, String sku, int quantity, String customer, String status, Instant createdAt) {
}
