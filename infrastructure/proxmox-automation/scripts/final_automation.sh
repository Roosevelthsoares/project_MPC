#!/bin/bash

echo "🎯 AUTOMAÇÃO FINAL - VM 732 na rede correta"
echo "=== Aguardando VM 732 em 192.168.90.20 ==="

# Aguardar VM 732 estar acessível na rede 192.168.90.x
echo "⏳ Testando conectividade com VM 732 em 192.168.90.20..."

for i in {1..30}; do
    if timeout 5 sshpass -p "MpC2025!" ssh -o StrictHostKeyChecking=no root@192.168.90.20 "echo 'VM-732-OK'" 2>/dev/null; then
        echo "🎉 VM 732 acessível em 192.168.90.20!"
        
        # Executar criação das VMs automaticamente
        echo "🚀 Criando VMs 701 e 702 via SSH..."
        sshpass -p "MpC2025!" ssh -o StrictHostKeyChecking=no root@192.168.90.20 "
        echo '📋 VMs atuais:'
        qm list
        
        echo ''
        echo '🚀 Criando VM 701 - pfSense (7 interfaces)...'
        qm create 701 \
          --name 'pfsense-firewall' \
          --memory 4096 \
          --cores 2 \
          --cpu host \
          --net0 virtio,bridge=vmbr0 \
          --net1 virtio,bridge=vmbr0 \
          --net2 virtio,bridge=vmbr0 \
          --net3 virtio,bridge=vmbr0 \
          --net4 virtio,bridge=vmbr0 \
          --net5 virtio,bridge=vmbr0 \
          --net6 virtio,bridge=vmbr0 \
          --scsi0 local-lvm:32 \
          --ostype other \
          --agent enabled=1 \
          2>/dev/null && echo '✅ VM 701 criada!' || echo '⚠️ VM 701 erro/já existe'
        
        echo ''
        echo '🛡️ Criando VM 702 - Security Onion (24GB RAM)...'
        qm create 702 \
          --name 'security-onion' \
          --memory 24576 \
          --cores 8 \
          --cpu host \
          --net0 virtio,bridge=vmbr0 \
          --net1 virtio,bridge=vmbr0 \
          --scsi0 local-lvm:200 \
          --scsi1 local-lvm:500 \
          --ostype l26 \
          --agent enabled=1 \
          2>/dev/null && echo '✅ VM 702 criada!' || echo '⚠️ VM 702 erro/já existe'
        
        echo ''
        echo '👤 Configurando usuário terraform...'
        pveum user add terraform@pve --password 'Terraform123!' 2>/dev/null || echo 'Usuário já existe'
        pveum acl modify / --users terraform@pve --roles Administrator
        pveum user token add terraform@pve tofu-token --privsep 0 2>/dev/null || echo 'Token já existe'
        
        echo ''
        echo '📊 VMs criadas (701-799):'
        qm list | grep -E '70[1-9]|7[1-9][0-9]'
        
        echo ''
        echo '🎉 AUTOMAÇÃO COMPLETA!'
        echo 'VM 701: pfSense (7 interfaces)'
        echo 'VM 702: Security Onion (24GB RAM)'
        echo 'Acesso: https://192.168.90.20:8006'
        "
        
        exit 0
    fi
    echo "Tentativa $i/30... aguardando VM 732 em 192.168.90.20"
    sleep 10
done

echo "❌ Timeout: VM 732 não acessível em 192.168.90.20"
echo ""
echo "🔧 CONFIGURE A REDE DA VM 732 PARA:"
echo "IP: 192.168.90.20/24"
echo "Gateway: 192.168.90.1"
echo "DNS: 192.168.90.1"