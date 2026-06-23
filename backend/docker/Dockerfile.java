FROM eclipse-temurin:21-jdk-jammy

RUN apt-get update && apt-get install -y curl ca-certificates grep \
    && update-ca-certificates \
    && mkdir -p /usr/local/bin \
    && curl -L -o /usr/local/bin/checkstyle.jar \
       https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.3.4/checkstyle-10.3.4-all.jar \
    && curl -L -o /usr/local/bin/google_checks.xml \
       https://raw.githubusercontent.com/checkstyle/checkstyle/checkstyle-10.3.4/src/main/resources/google_checks.xml \
    && useradd --create-home --uid 1000 runner \
    && mkdir -p /runner/work \
    && chown -R runner:runner /runner \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /runner
USER runner
CMD ["sleep", "infinity"]
