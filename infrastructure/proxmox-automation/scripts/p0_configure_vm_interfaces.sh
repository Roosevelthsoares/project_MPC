#!/bin/bash

# 🌐 P0-1: Configuração de Interfaces de Rede VMs 100/101
# Finalizar configuração das interfaces de rede conforme VM 131
# Data: 28 de setembro de 2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌐 P0-1: CONFIGURAÇÃO DE INTERFACES VMs 100/101${NC}"
echo "=============================================="
echo ""

# Configurações baseadas na VM 131
VM754_HOST="192.168.91.101"
VM754_USER="root"
VM754_PASS="MpC2025!"

echo -e "${YELLOW}📋 PLANO DE CONFIGURAÇÃO:${NC}"
echo "========================"
echo "🔥 VM 100 (Firewall): 7 interfaces de rede"
echo "   - net0: vmbr0 (management)"
echo "   - net1: vmbr6001 (WAN)"  
echo "   - net2: vmbr1 (LAN1)"
echo "   - net3: vmbr6003 (LAN2)"
echo "   - net4: vmbr6004 (LAN3)"
echo "   - net5: vmbr5001 (DMZ1)"
echo "   - net6: vmbr5002 (DMZ2)"
echo ""
echo "🛡️ VM 101 (IDS): 2 interfaces de rede"
echo "   - net0: vmbr0 (management)"
echo "   - net1: vmbr6001 (monitoring)"
echo ""

read -p "Continuar com a configuração? (s/N): " confirm
if [[ $confirm != "s" && $confirm != "S" ]]; then
    echo "❌ Operação cancelada"
    exit 1
fi

echo -e "${GREEN}🚀 INICIANDO CONFIGURAÇÃO...${NC}"

# Função para verificar se interface já existe
check_interface() {
    local vm_id=$1
    local net_id=$2
    
    result=$(sshpass -p "$VM754_PASS" ssh -o StrictHostKeyChecking=no $VM754_USER@$VM754_HOST \
        "qm config $vm_id | grep -c 'net$net_id:' || echo '0'")
    echo $result
}

# Função para adicionar interface de rede
add_network_interface() {
    local vm_id=$1
    local net_id=$2
    local bridge=$3
    local description=$4
    
    echo -e "${YELLOW}➕ Adicionando interface net$net_id ($bridge) na VM $vm_id - $description${NC}"
    
    # Verificar se interface já existe
    if [[ $(check_interface $vm_id $net_id) -gt 0 ]]; then
        echo -e "${BLUE}ℹ️ Interface net$net_id já existe na VM $vm_id${NC}"
        return 0
    fi
    
    # Adicionar interface
    sshpass -p "$VM754_PASS" ssh -o StrictHostKeyChecking=no $VM754_USER@$VM754_HOST \
        "qm set $vm_id --net$net_id virtio,bridge=$bridge"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Interface net$net_id adicionada com sucesso${NC}"
    else
        echo -e "${RED}❌ Erro ao adicionar interface net$net_id${NC}"
        return 1
    fi
}

echo -e "${BLUE}🔥 CONFIGURANDO VM 100 (FIREWALL)${NC}"
echo "================================="

# VM 100 - Firewall (7 interfaces conforme VM 131)
add_network_interface 100 1 "vmbr6001" "WAN Interface"
add_network_interface 100 2 "vmbr1" "LAN1 Interface"
add_network_interface 100 3 "vmbr6003" "LAN2 Interface"
add_network_interface 100 4 "vmbr6004" "LAN3 Interface"
add_network_interface 100 5 "vmbr5001" "DMZ1 Interface"
add_network_interface 100 6 "vmbr5002" "DMZ2 Interface"

echo ""
echo -e "${BLUE}🛡️ CONFIGURANDO VM 101 (IDS)${NC}"
echo "=============================="

# VM 101 - IDS (2 interfaces)
add_network_interface 101 1 "vmbr6001" "Monitoring Interface"

echo ""
echo -e "${GREEN}📊 VERIFICAÇÃO FINAL${NC}"
echo "==================="

# Verificar configurações finais
echo -e "${YELLOW}🔍 Configuração final VM 100:${NC}"
sshpass -p "$VM754_PASS" ssh -o StrictHostKeyChecking=no $VM754_USER@$VM754_HOST \
    "qm config 100 | grep 'net[0-9]:' | sort"

echo ""
echo -e "${YELLOW}🔍 Configuração final VM 101:${NC}"
sshpass -p "$VM754_PASS" ssh -o StrictHostKeyChecking=no $VM754_USER@$VM754_HOST \
    "qm config 101 | grep 'net[0-9]:' | sort"

echo ""
echo -e "${GREEN}✅ CONFIGURAÇÃO DE INTERFACES CONCLUÍDA!${NC}"
echo "=========================================="
echo "🔥 VM 100: 7 interfaces configuradas (management + 6 operacionais)"
echo "🛡️ VM 101: 2 interfaces configuradas (management + monitoring)"
echo ""
echo -e "${BLUE}📋 PRÓXIMOS PASSOS:${NC}"
echo "- Instalar pfSense na VM 100"
echo "- Instalar Security Onion na VM 101"
echo "- Configurar regras de firewall"
echo "- Configurar monitoramento IDS"

# Salvar log da configuração
echo "$(date): Interfaces de rede configuradas - VM 100 (7 interfaces), VM 101 (2 interfaces)" >> /tmp/mpc_config.log