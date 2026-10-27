package com.cloudops360.orders;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {
    private final ChaosInterceptor chaos;

    public WebConfig(ChaosInterceptor chaos) {
        this.chaos = chaos;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(chaos).addPathPatterns("/api/orders/**", "/api/orders");
    }
}
