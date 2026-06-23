FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    fpc \
    build-essential \
    && useradd --create-home --uid 1000 runner \
    && mkdir -p /runner/work /tmp/fpc-lint-cache/units \
    && chown -R runner:runner /runner /tmp/fpc-lint-cache \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /runner

USER runner
CMD ["sleep", "infinity"]
