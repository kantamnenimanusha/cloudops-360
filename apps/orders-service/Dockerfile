FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /build

COPY pom.xml .
RUN mvn -B -ntp -q dependency:go-offline

COPY src ./src
RUN mvn -B -ntp -q package -DskipTests

# Download and validate a pinned OpenTelemetry Java agent.
ARG OTEL_AGENT_VERSION=2.33.1

RUN mkdir -p /opt/otel \
    && curl -fLsS --retry 3 \
       "https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_AGENT_VERSION}/opentelemetry-javaagent.jar" \
       -o /opt/otel/opentelemetry-javaagent.jar \
    && jar --list --file /opt/otel/opentelemetry-javaagent.jar >/dev/null

FROM eclipse-temurin:21-jre

RUN groupadd -g 10001 app \
    && useradd -u 10001 -g app -s /usr/sbin/nologin app

WORKDIR /app

COPY --from=build /build/target/orders-service-*.jar /app/app.jar
COPY --from=build --chown=10001:10001 /opt/otel/opentelemetry-javaagent.jar /opt/otel/opentelemetry-javaagent.jar

RUN chmod 644 /opt/otel/opentelemetry-javaagent.jar

ARG APP_VERSION=dev
ARG GIT_COMMIT=unknown

ENV APP_VERSION=$APP_VERSION \
    GIT_COMMIT=$GIT_COMMIT \
    JAVA_TOOL_OPTIONS="-javaagent:/opt/otel/opentelemetry-javaagent.jar -XX:MaxRAMPercentage=70" \
    OTEL_TRACES_EXPORTER=none \
    OTEL_METRICS_EXPORTER=none \
    OTEL_LOGS_EXPORTER=none

USER 10001

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
