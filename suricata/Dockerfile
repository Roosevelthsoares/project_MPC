FROM ubuntu:22.04 AS builder

# Instala dependências de compilação
RUN apt-get update && apt-get install -y \
    libpcre3-dev \
    libpcre2-dev \
    build-essential \
    autoconf \
    automake \
    libtool \
    libpcap-dev \
    libnet1-dev \
    libyaml-dev \
    libjansson-dev \
    libcap-ng-dev \
    libmagic-dev \
    libnss3-dev \
    libgeoip-dev \
    libmaxminddb-dev \
    liblua5.1-dev \
    libhiredis-dev \
    libevent-dev \
    pkg-config \
    libnetfilter-queue-dev \
    libnetfilter-log-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libprotobuf-c-dev \
    git \
    wget \
    zlib1g-dev \
    rustc \
    cargo \
    python3-pip \
    cmake \
    ninja-build \
    libssl-dev

# Clona e compila o Suricata com suporte ao Prometheus
WORKDIR /src

# Compila e instala librabbitmq primeiro
RUN git clone https://github.com/alanxz/rabbitmq-c.git && \
    cd rabbitmq-c && \
    git checkout v0.11.0 && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr .. && \
    cmake --build . && \
    make install

# Instala hiredis para Redis
RUN git clone https://github.com/redis/hiredis.git && \
    cd hiredis && \
    make && \
    make install && \
    ldconfig

# Compila e instala Suricata
RUN mkdir -p /usr/lib/suricata && \
    wget https://www.openinfosecfoundation.org/download/suricata-7.0.1.tar.gz && \
    tar xvf suricata-7.0.1.tar.gz && \
    cd suricata-7.0.1 && \
    ./configure \
        --prefix=/usr \
        --sysconfdir=/etc \
        --localstatedir=/var \
        --enable-prometheus \
        --enable-geoip \
        --enable-lua \
        --enable-nfqueue \
        --enable-nflog \
        --enable-rust \
        --enable-redis \
        --enable-rabbitmq \
        --enable-gccprotect \
        --enable-pie \
        --enable-prometheus=yes \
        LIBS="-lprotobuf-c" && \
    make -j$(nproc) && \
    make install && \
    make install-conf

FROM ubuntu:22.04

# Instala dependências de runtime e libhtp
RUN apt-get update && apt-get install -y \
    libhtp2 \
    libmaxminddb0 \
    libpcre2-8-0 \
    libpcap0.8 \
    libnet1 \
    libyaml-0-2 \
    libjansson4 \
    libmagic1 \
    libnss3 \
    libnetfilter-queue1 \
    libnetfilter-log1 \
    libprotobuf-c1 \
    libhiredis0.14 \
    librabbitmq4

# Copia os binários e libs necessárias
COPY --from=builder /usr/bin/suricata /usr/bin/
COPY --from=builder /usr/lib/suricata /usr/lib/suricata
COPY --from=builder /etc/suricata /etc/suricata

# Instala dependências de runtime
RUN apt-get update && apt-get install -y \
    python3-yaml \
    python3-pip \
    libpcre3 \
    libpcap0.8 \
    libnet1 \
    libyaml-0-2 \
    libjansson4 \
    libcap-ng0 \
    libmagic1 \
    libnss3 \
    libgeoip1 \
    liblua5.1-0 \
    libhiredis0.14 \
    libevent-2.1-7 \
    libnetfilter-queue1 \
    libnetfilter-log1 \
    libprotobuf-c1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/lib/suricata/rules

# Instala suricata-update
RUN pip3 install --no-cache-dir suricata-update

# Copy project suricata.yaml to ensure our metrics configuration is used
# (build context is ./suricata so the file is at ./suricata.yaml)
COPY suricata.yaml /etc/suricata/suricata.yaml

# Cria diretórios necessários
RUN mkdir -p /var/log/suricata /var/run/suricata /var/lib/suricata

# Configura permissões
RUN chmod 750 /var/log/suricata /var/run/suricata /var/lib/suricata

COPY suricata-wrapper.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/suricata-wrapper.sh

ENTRYPOINT ["/usr/local/bin/suricata-wrapper.sh"]