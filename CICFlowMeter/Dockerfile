FROM openjdk:8-jdk

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libpcap0.8 libpcap0.8-dev \
    wireshark-common \
    git unzip curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala dependência do Producer (RabbitMQ client)
RUN pip3 install pika

# Copia todo o projeto
COPY . /app/

# Dá permissão de execução
RUN chmod +x /app/watchdog.sh /app/gradlew

# Compila o .jar
RUN ./gradlew clean fatJar

# Copia o .jar para o local esperado
# RUN cp /app/build/libs/CICFlowMeter-fat.jar /CICFlowMeter-4.0.jar
RUN cp /app/build/libs/CICFlowMeter-fat.jar /app/CICFlowMeter-fat.jar


# Copia as libs nativas e o jnetpcap.jar
RUN mkdir -p /app/lib/native && \
    cp /app/jnetpcap/linux/jnetpcap-1.4.r1425/libjnetpcap.so /app/lib/native/libjnetpcap.so && \
    cp /app/jnetpcap/linux/jnetpcap-1.4.r1425/libjnetpcap-pcap100.so /app/lib/native/libjnetpcap-pcap100.so && \
    cp /app/jnetpcap/linux/jnetpcap-1.4.r1425/jnetpcap.jar /app/lib/jnetpcap.jar

# Volumes e variáveis de ambiente
VOLUME ["/pcaps", "/flows"]
ENV PCAPS_DIR=/pcaps
ENV FLOWS_DIR=/flows
ENV DELAY=5
ENV CONVERT_LINKTYPE=1

CMD ["/app/watchdog.sh"]


# # Etapa 1: Build Java com OpenJDK
# FROM openjdk:8-jdk AS builder

# WORKDIR /app

# RUN apt-get update && apt-get install -y git unzip curl && rm -rf /var/lib/apt/lists/*

# COPY . /app/

# RUN chmod +x gradlew && ./gradlew clean fatJar

# # Etapa 2: Imagem final limpa baseada em Python
# FROM python:3.12.3-slim

# WORKDIR /app

# # Evita interações e melhora performance do apt
# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt-get update && apt-get install -y \
#     openjdk-8-jre-headless \
#     python3 python3-pip \
#     libpcap0.8 libpcap0.8-dev \
#     wireshark-common \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# # Instala somente a dependência necessária
# RUN pip install pika

# # Copia apenas os arquivos necessários do build
# COPY --from=builder /app/build/libs/CICFlowMeter-fat.jar /app/
# COPY --from=builder /app/watchdog.sh /app/
# COPY --from=builder /app/jnetpcap/linux/jnetpcap-1.4.r1425/libjnetpcap.so /app/lib/native/libjnetpcap.so
# COPY --from=builder /app/jnetpcap/linux/jnetpcap-1.4.r1425/libjnetpcap-pcap100.so /app/lib/native/libjnetpcap-pcap100.so
# COPY --from=builder /app/jnetpcap/linux/jnetpcap-1.4.r1425/jnetpcap.jar /app/lib/jnetpcap.jar

# RUN chmod +x /app/watchdog.sh

# VOLUME ["/pcaps", "/flows"]

# ENV PCAPS_DIR=/pcaps
# ENV FLOWS_DIR=/flows
# ENV DELAY=5
# ENV CONVERT_LINKTYPE=0

# CMD ["/app/watchdog.sh"]



# FROM python:3.12.3-slim

# # Usa uma imagem oficial com Java 8
# FROM openjdk:8-jdk

# # Define o diretório de trabalho
# WORKDIR /app

# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt-get update && apt-get install -y \
#     git unzip curl \
#     python3 python3-pip \
#     libpcap0.8 libpcap0.8-dev \
#     wireshark-common \
#     && rm -rf /var/lib/apt/lists/*

# # Instala dependência do Producer (RabbitMQ client)
# RUN pip3 install pika

# # Copia todo o projeto
# COPY . /app/

# # Dá permissão de execução ao script após o COPY
# RUN chmod +x /app/watchdog.sh

# # Dá permissão e compila o fatJar
# RUN chmod +x /app/gradlew \
#     && cd /app && ./gradlew clean fatJar

# # Copia o .jar gerado
# RUN cp /app/build/libs/CICFlowMeter-fat.jar /app/

# # Copia as libs nativas e o jnetpcap.jar
# RUN mkdir -p /app/lib/native && \
#     cp /app/jnetpcap/linux/jnetpcap-1.4.r1425/libjnetpcap.so /app/lib/native/libjnetpcap.so && \
#     cp /app/jnetpcap/linux/jnetpcap-1.4.r1425/libjnetpcap-pcap100.so /app/lib/native/libjnetpcap-pcap100.so && \
#     cp /app/jnetpcap/linux/jnetpcap-1.4.r1425/jnetpcap.jar /app/lib/jnetpcap.jar




# # Define volumes
# VOLUME ["/pcaps", "/flows"]

# # Variáveis de ambiente padrão
# ENV PCAPS_DIR=/pcaps
# ENV FLOWS_DIR=/flows
# ENV DELAY=5
# ENV CONVERT_LINKTYPE=0

# # Comando padrão
# CMD ["/app/watchdog.sh"]
