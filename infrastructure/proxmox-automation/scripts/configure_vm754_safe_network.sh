#!/bin/bash

echo "🔒 CONFIGURAÇÃO SEGURA DE REDE - VM 754 (REPLICAÇÃO VM 131)"
echo "============================================================"
echo ""

VM_ID="754"
HOST="192.168.90.10"
PASSWORD="MpC@2025$"

echo "⏳ Aguardando VM 754 completar instalação..."
echo "Tempo estimado: 15-20 minutos"
echo ""

# Função para testar SSH
test_ssh() {
    local ip=$1
    timeout 10 sshpass -p "MpC2025!" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$ip "echo 'SSH_OK'" 2>/dev/null
}

# Aguardar instalação
echo "🔍 Procurando VM 754 na rede..."
for i in {1..40}; do
    echo -n "Tentativa $i/40... "
    
    # Verificar range de IPs possíveis
    for ip in 192.168.91.{100..120}; do
        if test_ssh "$ip" >/dev/null 2>&1; then
            VM754_IP="$ip"
            echo "✅ ENCONTRADA! IP: $ip"
            break 2
        fi
    done
    
    echo "aguardando..."
    sleep 30
done

if [ -z "$VM754_IP" ]; then
    echo "❌ VM 754 não encontrada na rede após 20 minutos"
    echo "Verifique manualmente no console do Proxmox"
    exit 1
fi

echo ""
echo "🎯 VM 754 INSTALADA E ACESSÍVEL!"
echo "IP: $VM754_IP"
echo ""

echo "📊 Verificando sistema..."
sshpass -p "MpC2025!" ssh -o StrictHostKeyChecking=no root@$VM754_IP "
echo 'Sistema:' \$(cat /etc/os-release | grep PRETTY_NAME)
echo 'Proxmox:' \$(pveversion)
echo 'Hostname:' \$(hostname)
echo 'Uptime:' \$(uptime)
"

echo ""
echo "💾 BACKUP DA CONFIGURAÇÃO ATUAL..."
sshpass -p "MpC2025!" ssh -o StrictHostKeyChecking=no root@$VM754_IP "
cp /etc/network/interfaces /etc/network/interfaces.backup
cp /etc/pve/storage.cfg /etc/pve/storage.cfg.backup
echo 'Backup criado!'
"

echo ""
echo "🌐 APLICANDO CONFIGURAÇÃO DE REDE DA VM 131 (FASE 1 - SEGURA)"
echo "============================================================="

# Aplicar configuração em fases, sempre mantendo acesso
sshpass -p "MpC2025!" ssh -o StrictHostKeyChecking=no root@$VM754_IP "
echo '🔧 FASE 1: Configurando interfaces base (mantendo acesso atual)'

# Backup atual
cp /etc/network/interfaces /etc/network/interfaces.original

# Criar nova configuração mantendo acesso via vmbr0
cat > /etc/network/interfaces << 'EONET'
# loopback
auto lo
iface lo inet loopback

# Management interface - MANTER SEMPRE ATIVO
auto vmbr0
iface vmbr0 inet dhcp
    bridge-ports ens18
    bridge-stp off
    bridge-fd 0
    # Interface para acesso remoto - NÃO ALTERAR

# Preparação para interfaces físicas da VM 131
auto ens19
iface ens19 inet manual

auto ens20  
iface ens20 inet manual

auto ens21
iface ens21 inet manual

# Módulos dummy para bridges virtuais
pre-up modprobe dummy
pre-up ip link add dummy1 type dummy
pre-up ip link add dummy2 type dummy  
pre-up ip link add dummy4 type dummy

# Bridge Virtual 1 (SECONIONGW) - VM 131
auto vmbr5001
iface vmbr5001 inet static
    address 127.0.0.101/32
    bridge-ports dummy1
    bridge-stp off
    bridge-fd 0

# Bridge Virtual 2 (SPAN) - VM 131  
auto vmbr5002
iface vmbr5002 inet static
    address 127.0.0.102/32
    bridge-ports dummy2
    bridge-stp off
    bridge-fd 0

# Bridge Virtual 3 (BACKBONE2) - VM 131
auto vmbr6004
iface vmbr6004 inet static
    address 127.0.0.140/32
    bridge-ports dummy4
    bridge-stp off
    bridge-fd 0

# Cleanup
post-down ip link del dummy1 2>/dev/null || true
post-down ip link del dummy2 2>/dev/null || true
post-down ip link del dummy4 2>/dev/null || true
EONET

echo '✅ FASE 1 completa - Bridges virtuais configuradas'
echo 'Testando conectividade...'
"

# Testar se ainda temos acesso
if test_ssh "$VM754_IP" >/dev/null 2>&1; then
    echo "✅ Acesso mantido após FASE 1!"
else
    echo "❌ Acesso perdido! Restaurando backup..."
    sshpass -p "MpC@2025!" ssh -o StrictHostKeyChecking=no root@$VM754_IP "
    cp /etc/network/interfaces.backup /etc/network/interfaces
    systemctl restart networking
    "
    exit 1
fi

echo ""
echo "🎯 CONFIGURAÇÃO FASE 1 COMPLETA!"
echo "VM 754 configurada com bridges virtuais da VM 131"
echo "Acesso remoto mantido via vmbr0"
echo ""
echo "📋 PRÓXIMOS PASSOS (executar manualmente quando necessário):"
echo "1. Adicionar interfaces físicas WAN/LAN quando hardware estiver pronto"
echo "2. Configurar storage extra-lvm"
echo "3. Criar VMs aninhadas 100 (Firewall) e 101 (IDS)"
echo ""
echo "💾 IP da VM 754: $VM754_IP"
echo "🔑 Senha: MpC2025!"
echo "🌐 Interface web: https://$VM754_IP:8006"