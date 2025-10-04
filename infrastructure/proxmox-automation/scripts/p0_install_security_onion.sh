#!/bin/bash

# 🛡️ P0-3: Instalação Security Onion na VM 101
# Automatizar download e instalação do Security Onion
# Data: 28 de setembro de 2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛡️ P0-3: INSTALAÇÃO SECURITY ONION NA VM 101${NC}"
echo "==========================================="
echo ""

# Configurações
VM754_HOST="192.168.91.101"
VM754_USER="root"
VM754_PASS="MpC2025!"
SECURITYONION_VM_ID="101"
SECURITYONION_VERSION="2.4.100"
SECURITYONION_ISO_URL="https://github.com/Security-Onion-Solutions/securityonion/releases/download/v${SECURITYONION_VERSION}/securityonion-${SECURITYONION_VERSION}.iso"
SECURITYONION_ISO_NAME="securityonion-${SECURITYONION_VERSION}.iso"

echo -e "${YELLOW}📋 INFORMAÇÕES DA INSTALAÇÃO:${NC}"
echo "============================"
echo "🎯 VM ID: $SECURITYONION_VM_ID"
echo "🛡️ Security Onion Version: $SECURITYONION_VERSION"
echo "📁 ISO: $SECURITYONION_ISO_NAME"
echo "🌐 Host: $VM754_HOST"
echo "💾 RAM: 24GB (necessário para Security Onion)"
echo "💽 Disk: 220GB (para logs e dados)"
echo ""

read -p "Continuar com a instalação do Security Onion? (s/N): " confirm
if [[ $confirm != "s" && $confirm != "S" ]]; then
    echo "❌ Operação cancelada"
    exit 1
fi

echo -e "${GREEN}🚀 INICIANDO INSTALAÇÃO SECURITY ONION...${NC}"

# Função para executar comando remoto
remote_exec() {
    sshpass -p "$VM754_PASS" ssh -o StrictHostKeyChecking=no $VM754_USER@$VM754_HOST "$1"
}

# 1. Verificar se VM 101 existe
echo -e "${YELLOW}🔍 Verificando VM 101...${NC}"
if ! remote_exec "qm status $SECURITYONION_VM_ID" >/dev/null 2>&1; then
    echo -e "${RED}❌ VM $SECURITYONION_VM_ID não encontrada. Execute primeiro a criação da VM.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ VM $SECURITYONION_VM_ID encontrada${NC}"

# 2. Verificar especificações da VM
echo -e "${YELLOW}🔍 Verificando especificações da VM...${NC}"
vm_memory=$(remote_exec "qm config $SECURITYONION_VM_ID | grep '^memory:' | cut -d' ' -f2")
vm_cores=$(remote_exec "qm config $SECURITYONION_VM_ID | grep '^cores:' | cut -d' ' -f2")

echo "RAM: ${vm_memory}MB, Cores: $vm_cores"

if [[ $vm_memory -lt 24576 ]]; then
    echo -e "${RED}❌ VM $SECURITYONION_VM_ID precisa ter pelo menos 24GB RAM${NC}"
    echo "Atual: ${vm_memory}MB, Necessário: 24576MB"
    exit 1
fi

echo -e "${GREEN}✅ Especificações da VM OK${NC}"

# 3. Verificar interfaces de rede
echo -e "${YELLOW}🔍 Verificando interfaces de rede...${NC}"
interfaces_count=$(remote_exec "qm config $SECURITYONION_VM_ID | grep -c 'net[0-9]:' || echo '0'")
echo "Interfaces encontradas: $interfaces_count"

if [[ $interfaces_count -lt 2 ]]; then
    echo -e "${RED}❌ VM $SECURITYONION_VM_ID precisa ter 2 interfaces de rede configuradas${NC}"
    echo "Execute primeiro: ./p0_configure_vm_interfaces.sh"
    exit 1
fi

echo -e "${GREEN}✅ Interfaces de rede OK (2 interfaces)${NC}"

# 4. Download da ISO Security Onion
echo -e "${YELLOW}📥 Fazendo download da ISO Security Onion...${NC}"
remote_exec "
    cd /var/lib/vz/template/iso/
    
    # Verificar se ISO já existe
    if [[ -f '$SECURITYONION_ISO_NAME' ]]; then
        echo 'ISO Security Onion já existe'
    else
        echo 'Fazendo download da ISO Security Onion...'
        echo 'Isso pode levar alguns minutos (ISO ~2.5GB)...'
        wget -q --show-progress '$SECURITYONION_ISO_URL' -O '$SECURITYONION_ISO_NAME'
        
        echo 'Download concluído!'
    fi
    
    ls -lh '$SECURITYONION_ISO_NAME'
"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ ISO Security Onion pronta${NC}"
else
    echo -e "${RED}❌ Erro no download da ISO${NC}"
    exit 1
fi

# 5. Configurar ISO na VM
echo -e "${YELLOW}💿 Configurando ISO na VM 101...${NC}"
remote_exec "qm set $SECURITYONION_VM_ID --ide2 local:iso/$SECURITYONION_ISO_NAME,media=cdrom"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ ISO configurada na VM${NC}"
else
    echo -e "${RED}❌ Erro ao configurar ISO${NC}"
    exit 1
fi

# 6. Configurar boot order
echo -e "${YELLOW}🚀 Configurando boot order...${NC}"
remote_exec "qm set $SECURITYONION_VM_ID --boot order=ide2,scsi0"

# 7. Parar VM se estiver rodando
echo -e "${YELLOW}⏹️ Parando VM 101 se estiver rodando...${NC}"
remote_exec "qm stop $SECURITYONION_VM_ID" 2>/dev/null || true
sleep 3

# 8. Iniciar VM para instalação
echo -e "${YELLOW}▶️ Iniciando VM 101 para instalação...${NC}"
remote_exec "qm start $SECURITYONION_VM_ID"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ VM 101 iniciada com Security Onion ISO${NC}"
else
    echo -e "${RED}❌ Erro ao iniciar VM${NC}"
    exit 1
fi

# 9. Instruções finais
echo ""
echo -e "${GREEN}🎉 INSTALAÇÃO SECURITY ONION INICIADA!${NC}"
echo "====================================="
echo ""
echo -e "${BLUE}📋 PRÓXIMOS PASSOS MANUAIS:${NC}"
echo "=========================="
echo "1. 🖥️ Acesse o console da VM 101:"
echo "   - Web: https://$VM754_HOST:8006"
echo "   - VM ID: $SECURITYONION_VM_ID"
echo ""
echo "2. 🔧 Durante a instalação:"
echo "   - Escolha 'Install Security Onion'"
echo "   - Username: souser"
echo "   - Password: escolha uma senha forte"
echo "   - Configure disco: /dev/sda (220GB)"
echo "   - Aguarde instalação completa (~30-45 min)"
echo ""
echo "3. 🌐 Configuração inicial de rede:"
echo "   - Management: ens3 (vmbr0)"
echo "   - Monitor: ens4 (vmbr6001)"
echo "   - Configure IP management"
echo ""
echo "4. 🛡️ Configuração de sensores:"
echo "   - Tipo: Standalone"
echo "   - Interface de monitoramento: ens4"
echo "   - Configurar regras Suricata"
echo ""
echo "5. 🔑 Acesso pós-instalação:"
echo "   - SSH: souser@IP_MANAGEMENT"
echo "   - Web: https://IP_MANAGEMENT"
echo "   - SOC: https://IP_MANAGEMENT/login"
echo ""
echo -e "${YELLOW}⏱️ TEMPO ESTIMADO: 45-60 minutos${NC}"
echo ""
echo -e "${BLUE}🔍 MONITORAR INSTALAÇÃO:${NC}"
echo "ssh $VM754_USER@$VM754_HOST 'qm monitor $SECURITYONION_VM_ID'"

# Salvar log
echo "$(date): Security Onion ISO configurada e VM 101 iniciada para instalação" >> /tmp/mpc_config.log

echo ""
echo -e "${GREEN}✅ SCRIPT P0-3 CONCLUÍDO!${NC}"
echo "========================="
echo "Instalação Security Onion em andamento na VM 101"
echo ""
echo -e "${BLUE}📚 DOCUMENTAÇÃO ADICIONAL:${NC}"
echo "- Security Onion: https://docs.securityonion.net/"
echo "- Configuração: https://docs.securityonion.net/en/2.4/installation.html"