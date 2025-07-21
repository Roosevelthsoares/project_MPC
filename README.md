# Project MPC

## Visão Geral

Este repositório contém a integração de um pipeline ponta-a-ponta para análise de tráfego de rede e predição de anomalias utilizando:

1. **CICFlowMeter**
   - Monitora arquivos `.pcap` em um diretório configurado
   - Conecta ao RabbitMQ, aguardando o broker ficar pronto antes de enviar mensagens
   - Processa cada `.pcap`, extrai um vetor de 78 features por fluxo
   - Publica um JSON com as 78 variáveis no RabbitMQ
   - Remove o arquivo `.pcap` original após o processamento, sinalizando sucesso

2. **RabbitMQ**
   - Atua como broker de mensagens para desacoplar o coletor de features e o serviço de predição

3. **Oráculo**
   - Carrega o dataset de treinamento (shape: 363163 amostras × 78 features)
   - Conecta ao RabbitMQ e fica “à escuta” de novas mensagens JSON
   - Recebe o array de 78 floats (aviso de nomes de features ignorado pelo `StandardScaler`)
   - Aplica transformação de escala com `StandardScaler`
   - Executa predição usando o modelo Mixture of Experts (MoE)
   - Retorna ou registra o resultado da predição

## Estado Atual

- Pipeline CICFlowMeter → RabbitMQ → Oráculo está 100% operacional
- Serviços definidos em `docker-compose.yml`:
  - `rabbitmq`
  - `cicflowmeter`
  - `oraculo`
- Modelo de ML integrado e validado no fluxo de dados real
- Logs de debug ainda via `print` no Oráculo

## Tecnologias Utilizadas

- **CICFlowMeter** (extração de features de tráfego)
- **RabbitMQ** (mensageria)
- **Python 3**, **Scikit-Learn** (pré-processamento e predição)
- **Docker & Docker Compose** (orquestração dos serviços)

## Próximos Passos

- Persistir resultados de predição em **Logstash** / **Elasticsearch** / **Kibana**
- Refatorar logging: substituir `print` por `logging` com níveis configuráveis
- Instrumentar métricas e alertas (latência de processamento, erros de parsing)

## Como Testar

1. **Pré-requisitos**
   - Docker & Docker Compose instalados
   - Um arquivo PCAP de teste (por exemplo, `sample.pcap`)

2. **Clonar repositório**

   ```bash
   git clone https://github.com/Roosevelthsoares/project_MPC.git
   cd project_MPC
   ```

3. **Subir os serviços**

   ```bash
   docker-compose up --build -d
   ```

4. **Verificar containers em execução**

   ```bash
   docker ps
   ```

5. **Inserir PCAP para processamento**

   ```bash
   # Copie o arquivo de teste para o diretório de PCAPs monitorado pelo CICFlowMeter
   cp /caminho/para/sample.pcap CICFlowMeter/pcaps/
   ```

   O CICFlowMeter detectará o arquivo, processará o fluxo, publicará as features no RabbitMQ e removerá o PCAP quando concluir.

6. **Acompanhar logs**

   - **CICFlowMeter**:
     ```bash
     docker-compose logs -f cicflowmeter
     ```

   - **Oráculo**:
     ```bash
     docker-compose logs -f oraculo
     ```

   Você deverá ver algo como:
   ```text
   Prediction: <valor>
   ```

7. **Encerrar os serviços**

   ```bash
   docker-compose down
   ```

8. **Limpeza opcional**

   - Remova volumes e imagens não usados:
     ```bash
     docker system prune -f
     docker volume prune -f
     ```
