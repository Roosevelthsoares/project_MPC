#!/bin/bash

# Script para criar VMs aninhadas na VM 732 (Proxmox)
# VM 100: pfSense (Firewall) com 7 interfaces de rede
# VM 101: Security Onion com 24GB RAM

echo "=== Criação das VMs Aninhadas 100 e 101 ==="
echo ""

# Informações da VM 732
VM732_IP="192.168.100.28"
VM732_PASSWORD="MpC2025!"

echo "🎯 ALVO: VM 732 - Proxmox"
echo "📍 IP: $VM732_IP"
echo "🔑 Senha: $VM732_PASSWORD"
echo ""

echo "📋 VMs a serem criadas:"
echo "   📡 VM 100: pfSense (Firewall)"
echo "       - 4GB RAM, 2 CPU cores"
echo "       - 7 interfaces de rede (conforme VM 131)"
echo "       - 32GB disco"
echo ""
echo "   🛡️  VM 101: Security Onion"
echo "       - 24GB RAM, 4 CPU cores"
echo "       - 2 interfaces de rede"
echo "       - 200GB disco"
echo ""

# Função para testar SSH
test_ssh() {
    if sshpass -p "$VM732_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$VM732_IP "echo 'SSH OK'" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

echo "🔐 Testando acesso SSH..."
if test_ssh; then
    echo "✅ SSH disponível! Criando VMs..."
    
    # Criar VM 100 - pfSense
    echo ""
    echo "📡 Criando VM 100 (pfSense)..."
    sshpass -p "$VM732_PASSWORD" ssh -o StrictHostKeyChecking=no root@$VM732_IP "
    qm create 100 \
      --name 'pfSense-Firewall' \
      --memory 4096 \
      --cores 2 \
      --cpu host \
      --sockets 1 \
      --ostype other \
      --scsihw virtio-scsi-pci \
      --scsi0 local-lvm:32 \
      --net0 virtio,bridge=vmbr0 \
      --net1 virtio,bridge=vmbr1 \
      --net2 virtio,bridge=vmbr2 \
      --net3 virtio,bridge=vmbr3 \
      --net4 virtio,bridge=vmbr4 \
      --net5 virtio,bridge=vmbr5 \
      --net6 virtio,bridge=vmbr6 \
      --boot order=scsi0 \
      --onboot 0
    echo 'VM 100 (pfSense) criada!'
    "
    
    # Criar VM 101 - Security Onion
    echo ""
    echo "🛡️  Criando VM 101 (Security Onion)..."
    sshpass -p "$VM732_PASSWORD" ssh -o StrictHostKeyChecking=no root@$VM732_IP "
    qm create 101 \
      --name 'Security-Onion' \
      --memory 24576 \
      --cores 4 \
      --cpu host \
      --sockets 1 \
      --ostype l26 \
      --scsihw virtio-scsi-pci \
      --scsi0 local-lvm:200 \
      --net0 virtio,bridge=vmbr0 \
      --net1 virtio,bridge=vmbr1 \
      --boot order=scsi0 \
      --onboot 0
    echo 'VM 101 (Security Onion) criada!'
    "
    
    echo ""
    echo "🎉 VMs ANINHADAS CRIADAS COM SUCESSO!"
    echo ""
    echo "📋 RESUMO:"
    echo "   ✅ VM 732: Proxmox VE (Host das VMs aninhadas)"
    echo "   ✅ VM 100: pfSense (7 interfaces de rede)"
    echo "   ✅ VM 101: Security Onion (24GB RAM)"
    echo ""
    echo "🔗 ACESSO:"
    echo "   🌐 Proxmox VM 732: https://$VM732_IP:8006"
    echo "   🔑 Login: root / $VM732_PASSWORD"
    echo ""
    echo "🎯 PRÓXIMOS PASSOS MANUAIS:"
    echo "   1. Fazer upload das ISOs do pfSense e Security Onion"
    echo "   2. Configurar as VMs 100 e 101 com as ISOs"
    echo "   3. Instalar e configurar os sistemas"
    echo "   4. Configurar rede entre as VMs"
    echo ""
    echo "✅ REPLICAÇÃO DA VM 131 CONCLUÍDA!"
    
else
    echo "❌ SSH não disponível ainda"
    echo ""
    echo "📋 CONFIGURAÇÃO MANUAL NECESSÁRIA:"
    echo "   1. 🌐 Acesse: https://$VM732_IP:8006"
    echo "   2. 🔑 Login: root / $VM732_PASSWORD"
    echo "   3. ⚙️  Configure usuário terraform se necessário"
    echo "   4. 📁 Faça upload das ISOs necessárias"
    echo "   5. 🖥️  Crie as VMs 100 e 101 manualmente"
    echo ""
    echo "🎯 COMANDOS PARA VMs (execute no Proxmox VM 732):"
    echo ""
    echo "# VM 100 - pfSense:"
    echo "qm create 100 --name 'pfSense-Firewall' --memory 4096 --cores 2 --scsi0 local-lvm:32 --net0 virtio,bridge=vmbr0 --net1 virtio,bridge=vmbr1 --net2 virtio,bridge=vmbr2 --net3 virtio,bridge=vmbr3 --net4 virtio,bridge=vmbr4 --net5 virtio,bridge=vmbr5 --net6 virtio,bridge=vmbr6"
    echo ""
    echo "# VM 101 - Security Onion:"
    echo "qm create 101 --name 'Security-Onion' --memory 24576 --cores 4 --scsi0 local-lvm:200 --net0 virtio,bridge=vmbr0 --net1 virtio,bridge=vmbr1"
    echo ""
fi

# Salvar informações finais
cat > /home/rts/mpc-iac/vm732_final_info.env << EOF
# Informações da VM 732 - Replicação da VM 131
VM732_IP=$VM732_IP
VM732_PASSWORD=$VM732_PASSWORD
VM732_URL=https://$VM732_IP:8006

# VMs Aninhadas planejadas
VM100_NAME="pfSense-Firewall"
VM100_RAM="4096"
VM100_CORES="2"
VM100_NETWORKS="7"

VM101_NAME="Security-Onion"
VM101_RAM="24576" 
VM101_CORES="4"
VM101_NETWORKS="2"

# Status do projeto
PROJECT_STATUS="VM 732 operacional - VMs aninhadas prontas para criação"
NEXT_STEPS="Upload ISOs, configurar VMs 100/101, instalação dos sistemas"
EOF

echo ""
echo "💾 Informações completas salvas em: vm732_final_info.env"