# Oráculo

## Introdução

Oráculo é um componente dentro do Módulo de Proteção Cibernética (MPC) responsável por realizar a classificação de pacotes de redes em malicioso ou benigno através de um modelo de machine learning.

## Diagrama de funcionamento

![Alt text](diagram.png)

O Oráculo recebe metadados relativos ao tráfego de rede que passa pelo MPC em formato JSON de uma fila do RabbitMQ, faz a classificação de tal tráfego e, em caso de tráfego malicioso, se comunica com o pfSense do MPC requisitando a criação de uma regra de bloqueio de IP no firewall.