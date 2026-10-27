package com.cloudops360.orders;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateOrderRequest(
        @NotBlank @Size(max = 40) String sku,
        @Min(1) @Max(1000) int quantity,
        @NotBlank @Size(max = 80) String customer) {
}
