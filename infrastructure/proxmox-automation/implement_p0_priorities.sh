#!/bin/bash

# 🎯 PRÓXIMOS PASSOS PRIORITÁRIOS (P0) - MPC 1.0
# Script para implementar melhorias críticas identificadas
# Data: 28 de setembro de 2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 PRÓXIMOS PASSOS PRIORITÁRIOS (P0) - MPC 1.0${NC}"
echo "==============================================="
echo ""

# Carregar configurações
if [[ -f "infrastructure/proxmox-automation/configs/validated_configs.env" ]]; then
    source infrastructure/proxmox-automation/configs/validated_configs.env
    echo -e "${GREEN}✅ Configurações carregadas${NC}"
else
    echo -e "${RED}❌ Arquivo de configurações não encontrado${NC}"
    exit 1
fi

echo -e "${PURPLE}📋 LISTA DE PRIORIDADES P0:${NC}"
echo "================================"
echo "1. 🌐 Finalizar configuração de interfaces VMs 100/101"
echo "2. 🔥 Instalar pfSense na VM 100"
echo "3. 🛡️ Instalar Security Onion na VM 101"
echo "4. 🤖 Criar Ansible Playbooks para automação"
echo "5. 💾 Implementar backup automatizado"
echo ""

read -p "Escolha qual tarefa implementar (1-5): " choice

case $choice in
    1)
        echo -e "${YELLOW}🌐 IMPLEMENTANDO: Configuração de interfaces VMs 100/101${NC}"
        ./scripts/p0_configure_vm_interfaces.sh
        ;;
    2)
        echo -e "${YELLOW}🔥 IMPLEMENTANDO: Instalação pfSense VM 100${NC}"
        ./scripts/p0_install_pfsense.sh
        ;;
    3)
        echo -e "${YELLOW}🛡️ IMPLEMENTANDO: Instalação Security Onion VM 101${NC}"
        ./scripts/p0_install_security_onion.sh
        ;;
    4)
        echo -e "${YELLOW}🤖 IMPLEMENTANDO: Ansible Playbooks${NC}"
        ./scripts/p0_create_ansible_playbooks.sh
        ;;
    5)
        echo -e "${YELLOW}💾 IMPLEMENTANDO: Backup automatizado${NC}"
        ./scripts/p0_implement_backup.sh
        ;;
    *)
        echo -e "${RED}❌ Opção inválida${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}"
echo "✅ TAREFA P0 IMPLEMENTADA COM SUCESSO!"
echo "======================================"
echo "📋 Para próxima tarefa, execute novamente este script"
echo "📚 Documentação atualizada em README.md"
echo -e "${NC}"