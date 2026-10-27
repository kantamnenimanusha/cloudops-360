package com.cloudops360.orders;

import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

import io.micrometer.core.instrument.MeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    private final Map<String, Order> orders = new ConcurrentHashMap<>();
    private final InventoryClient inventory;
    private final MeterRegistry meters;

    public OrderService(InventoryClient inventory, MeterRegistry meters) {
        this.inventory = inventory;
        this.meters = meters;
    }

    public Order create(CreateOrderRequest request) {
        try {
            inventory.reserve(request.sku(), request.quantity());
        } catch (InventoryException e) {
            meters.counter("orders_rejected_total", "reason", e.kind().name().toLowerCase()).increment();
            log.warn("order rejected sku={} reason={}", request.sku(), e.kind());
            throw e;
        }
        Order order = new Order(UUID.randomUUID().toString(), request.sku(), request.quantity(),
                request.customer(), "CONFIRMED", Instant.now());
        orders.put(order.id(), order);
        meters.counter("orders_created_total").increment();
        log.info("order created id={} sku={} quantity={}", order.id(), order.sku(), order.quantity());
        return order;
    }

    public List<Order> list() {
        return orders.values().stream().sorted(Comparator.comparing(Order::createdAt).reversed()).toList();
    }

    public Optional<Order> find(String id) {
        return Optional.ofNullable(orders.get(id));
    }
}
