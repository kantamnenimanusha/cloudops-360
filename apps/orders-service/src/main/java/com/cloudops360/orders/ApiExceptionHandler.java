package com.cloudops360.orders;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(InventoryException.class)
    public ProblemDetail inventory(InventoryException e) {
        HttpStatus status = switch (e.kind()) {
            case UNKNOWN_SKU -> HttpStatus.NOT_FOUND;
            case INSUFFICIENT_STOCK -> HttpStatus.CONFLICT;
            case UNAVAILABLE -> HttpStatus.SERVICE_UNAVAILABLE;
        };
        return ProblemDetail.forStatusAndDetail(status, e.getMessage());
    }
}
