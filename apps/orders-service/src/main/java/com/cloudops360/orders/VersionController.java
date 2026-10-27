package com.cloudops360.orders;

import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class VersionController {
    private final String version;
    private final String commit;

    public VersionController(@Value("${app.version:dev}") String version, @Value("${app.commit:unknown}") String commit) {
        this.version = version;
        this.commit = commit;
    }

    @GetMapping("/api/version")
    public Map<String, String> version() {
        return Map.of("service", "orders-service", "version", version, "commit", commit);
    }
}
