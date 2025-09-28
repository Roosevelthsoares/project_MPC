#!/bin/bash

# 🚀 Script Principal de Automação Proxmox
# Projeto MPC 1.0 - Automação completa de infraestrutura
# Data: 28 de setembro de 2025
# Status: VALIDADO E FUNCIONANDO 100% ✅

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 INICIANDO AUTOMAÇÃO COMPLETA PROXMOX${NC}"
echo "=================================================="

# Verificar se estamos no diretório correto
if [[ ! -f "configs/validated_configs.env" ]]; then
    echo -e "${RED}❌ Erro: Execute este script do diretório proxmox-automation${NC}"
    exit 1
fi

# Carregar configurações validadas
echo -e "${YELLOW}📋 Carregando configurações...${NC}"
source configs/validated_configs.env

# Verificar conectividade com Proxmox
echo -e "${YELLOW}🔍 Verificando conectividade com Proxmox...${NC}"
if ! ping -c 1 ${PROXMOX_HOST} >/dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Não foi possível conectar ao Proxmox host ${PROXMOX_HOST}${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Conectividade OK${NC}"

# Menu de opções
echo -e "${BLUE}"
echo "📋 OPÇÕES DE AUTOMAÇÃO:"
echo "======================"
echo "1. Validação completa da automação (recomendado)"
echo "2. Criar VM principal (732) com VMs aninhadas"
echo "3. Replicar configuração VM 131 completa"
echo "4. Validar VMs existentes"
echo "5. Relatório de status completo"
echo -e "${NC}"

read -p "Escolha uma opção (1-5): " option

case $option in
    1)
        echo -e "${GREEN}🎯 Executando validação completa...${NC}"
        ./scripts/complete_auto_validation.sh
        ;;
    2)
        echo -e "${GREEN}🏗️ Criando VM principal com VMs aninhadas...${NC}"
        ./scripts/create_nested_vms_final.sh
        ;;
    3)
        echo -e "${GREEN}🔄 Replicando configuração VM 131...${NC}"
        ./scripts/configure_vm754_safe_network.sh
        ;;
    4)
        echo -e "${GREEN}✅ Validando VMs existentes...${NC}"
        ./scripts/final_check_vm732.sh
        ;;
    5)
        echo -e "${GREEN}📊 Gerando relatório de status...${NC}"
        ./scripts/validation_success_report.sh
        ;;
    *)
        echo -e "${RED}❌ Opção inválida${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}"
echo "🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=================================="
echo "✅ Para mais informações, consulte o README.md"
echo "✅ Logs detalhados disponíveis nos scripts individuais"
echo "✅ Acesso web: https://192.168.90.20:8006 (VM 732)"
echo "✅ Credenciais: root/MpC2025!"
echo -e "${NC}"