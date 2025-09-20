# ./pcap-feeder/Dockerfile
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    netsniff-ng inotify-tools iproute2 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# entrypoint does: start netsniff-ng (flow-aware), then hard-link fanout
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
