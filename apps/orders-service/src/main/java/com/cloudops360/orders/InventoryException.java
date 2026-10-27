package com.cloudops360.orders;

/** Failures talking to inventory-service, mapped to HTTP statuses by {@link ApiExceptionHandler}. */
public class InventoryException extends RuntimeException {
    public enum Kind { UNKNOWN_SKU, INSUFFICIENT_STOCK, UNAVAILABLE }

    private final Kind kind;

    public InventoryException(Kind kind, String message) {
        super(message);
        this.kind = kind;
    }

    public Kind kind() {
        return kind;
    }
}
