#!/bin/bash

# 🔥 P0-2: Instalação pfSense na VM 100
# Automatizar download e instalação do pfSense
# Data: 28 de setembro de 2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔥 P0-2: INSTALAÇÃO PFSENSE NA VM 100${NC}"
echo "====================================="
echo ""

# Configurações
VM754_HOST="192.168.91.101"
VM754_USER="root"
VM754_PASS="MpC2025!"
PFSENSE_VM_ID="100"
PFSENSE_VERSION="2.7.2"
PFSENSE_ISO_URL="https://sgpfiles.netgate.com/mirror/downloads/pfSense-CE-${PFSENSE_VERSION}-RELEASE-amd64.iso.gz"
PFSENSE_ISO_NAME="pfSense-CE-${PFSENSE_VERSION}-RELEASE-amd64.iso"

echo -e "${YELLOW}📋 INFORMAÇÕES DA INSTALAÇÃO:${NC}"
echo "============================"
echo "🎯 VM ID: $PFSENSE_VM_ID"
echo "🔥 pfSense Version: $PFSENSE_VERSION"
echo "📁 ISO: $PFSENSE_ISO_NAME"
echo "🌐 Host: $VM754_HOST"
echo ""

read -p "Continuar com a instalação do pfSense? (s/N): " confirm
if [[ $confirm != "s" && $confirm != "S" ]]; then
    echo "❌ Operação cancelada"
    exit 1
fi

echo -e "${GREEN}🚀 INICIANDO INSTALAÇÃO PFSENSE...${NC}"

# Função para executar comando remoto
remote_exec() {
    sshpass -p "$VM754_PASS" ssh -o StrictHostKeyChecking=no $VM754_USER@$VM754_HOST "$1"
}

# 1. Verificar se VM 100 existe
echo -e "${YELLOW}🔍 Verificando VM 100...${NC}"
if ! remote_exec "qm status $PFSENSE_VM_ID" >/dev/null 2>&1; then
    echo -e "${RED}❌ VM $PFSENSE_VM_ID não encontrada. Execute primeiro a criação da VM.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ VM $PFSENSE_VM_ID encontrada${NC}"

# 2. Verificar interfaces de rede
echo -e "${YELLOW}🔍 Verificando interfaces de rede...${NC}"
interfaces_count=$(remote_exec "qm config $PFSENSE_VM_ID | grep -c 'net[0-9]:' || echo '0'")
echo "Interfaces encontradas: $interfaces_count"

if [[ $interfaces_count -lt 7 ]]; then
    echo -e "${RED}❌ VM $PFSENSE_VM_ID precisa ter 7 interfaces de rede configuradas${NC}"
    echo "Execute primeiro: ./p0_configure_vm_interfaces.sh"
    exit 1
fi

echo -e "${GREEN}✅ Interfaces de rede OK (7 interfaces)${NC}"

# 3. Download da ISO pfSense
echo -e "${YELLOW}📥 Fazendo download da ISO pfSense...${NC}"
remote_exec "
    cd /var/lib/vz/template/iso/
    
    # Verificar se ISO já existe
    if [[ -f '$PFSENSE_ISO_NAME' ]]; then
        echo 'ISO pfSense já existe'
    else
        echo 'Fazendo download da ISO pfSense...'
        wget -q --show-progress '$PFSENSE_ISO_URL' -O '${PFSENSE_ISO_NAME}.gz'
        
        echo 'Descompactando ISO...'
        gunzip '${PFSENSE_ISO_NAME}.gz'
        
        echo 'Download concluído!'
    fi
    
    ls -lh '$PFSENSE_ISO_NAME'
"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ ISO pfSense pronta${NC}"
else
    echo -e "${RED}❌ Erro no download da ISO${NC}"
    exit 1
fi

# 4. Configurar ISO na VM
echo -e "${YELLOW}💿 Configurando ISO na VM 100...${NC}"
remote_exec "qm set $PFSENSE_VM_ID --ide2 local:iso/$PFSENSE_ISO_NAME,media=cdrom"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ ISO configurada na VM${NC}"
else
    echo -e "${RED}❌ Erro ao configurar ISO${NC}"
    exit 1
fi

# 5. Configurar boot order
echo -e "${YELLOW}🚀 Configurando boot order...${NC}"
remote_exec "qm set $PFSENSE_VM_ID --boot order=ide2,scsi0"

# 6. Parar VM se estiver rodando
echo -e "${YELLOW}⏹️ Parando VM 100 se estiver rodando...${NC}"
remote_exec "qm stop $PFSENSE_VM_ID" 2>/dev/null || true
sleep 3

# 7. Iniciar VM para instalação
echo -e "${YELLOW}▶️ Iniciando VM 100 para instalação...${NC}"
remote_exec "qm start $PFSENSE_VM_ID"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ VM 100 iniciada com pfSense ISO${NC}"
else
    echo -e "${RED}❌ Erro ao iniciar VM${NC}"
    exit 1
fi

# 8. Instruções finais
echo ""
echo -e "${GREEN}🎉 INSTALAÇÃO PFSENSE INICIADA!${NC}"
echo "================================"
echo ""
echo -e "${BLUE}📋 PRÓXIMOS PASSOS MANUAIS:${NC}"
echo "=========================="
echo "1. 🖥️ Acesse o console da VM 100:"
echo "   - Web: https://$VM754_HOST:8006"
echo "   - VM ID: $PFSENSE_VM_ID"
echo ""
echo "2. 🔧 Durante a instalação:"
echo "   - Escolha 'Install pfSense'"
echo "   - Aceite configurações padrão"
echo "   - Configure disco: ada0 (32GB)"
echo "   - Aguarde instalação completa"
echo ""
echo "3. 🌐 Configuração inicial de rede:"
echo "   - WAN: vtnet1 (vmbr6001)"
echo "   - LAN: vtnet2 (vmbr1)"
echo "   - Configurar IPs das interfaces"
echo ""
echo "4. 🔑 Acesso pós-instalação:"
echo "   - Console: VM 100 direct"
echo "   - Web: https://IP_LAN:443"
echo "   - User: admin / Password: pfsense"
echo ""
echo -e "${YELLOW}⏱️ TEMPO ESTIMADO: 15-20 minutos${NC}"
echo ""
echo -e "${BLUE}🔍 MONITORAR INSTALAÇÃO:${NC}"
echo "ssh $VM754_USER@$VM754_HOST 'qm monitor $PFSENSE_VM_ID'"

# Salvar log
echo "$(date): pfSense ISO configurada e VM 100 iniciada para instalação" >> /tmp/mpc_config.log

echo ""
echo -e "${GREEN}✅ SCRIPT P0-2 CONCLUÍDO!${NC}"
echo "========================"
echo "Instalação pfSense em andamento na VM 100"