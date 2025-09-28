#!/bin/bash

echo "🎯 VALIDAÇÃO COMPLETA - INSTALAÇÃO AUTOMÁTICA + SSH"
echo "=== CRIANDO ANSWER FILE QUE REALMENTE FUNCIONA ==="

# Parar VM 753 atual
sshpass -p "MpC@2025$" ssh -o StrictHostKeyChecking=no root@192.168.90.10 "
echo '🛑 Parando VM 753 atual...'
qm stop 753 2>/dev/null || true
qm destroy 753 --purge 2>/dev/null || true
"

echo ""
echo "📝 Criando answer file MINIMAL e funcional..."

# Criar answer file super simples baseado na documentação oficial
cat > /tmp/answer-minimal.toml << 'EOF'
[global]
keyboard = "en-us"
country = "US"
fqdn = "pve753.local"
mailto = "admin@pve753.local"
timezone = "America/Sao_Paulo"
root_password = "MpC2025!"

[network]
source = "from-dhcp"

[disk-setup]
filesystem = "ext4"
disk_list = ["sda"]
EOF

echo "✅ Answer file MINIMAL criado:"
cat /tmp/answer-minimal.toml

echo ""
echo "🔨 Enviando para Proxmox e criando ISO..."
sshpass -p "MpC@2025$" scp -o StrictHostKeyChecking=no /tmp/answer-minimal.toml root@192.168.90.10:/tmp/

sshpass -p "MpC@2025$" ssh -o StrictHostKeyChecking=no root@192.168.90.10 "
echo '🛠️ Criando ISO com answer file MINIMAL...'
proxmox-auto-install-assistant prepare-iso --fetch-from iso --answer-file /tmp/answer-minimal.toml --output /var/lib/vz/template/iso/proxmox-minimal.iso /var/lib/vz/template/iso/proxmox-ve_8.4-1.iso

echo '✅ Verificando ISO criada:'
ls -la /var/lib/vz/template/iso/proxmox-minimal.iso

if [ -f '/var/lib/vz/template/iso/proxmox-minimal.iso' ]; then
    echo '✅ ISO criada com sucesso!'
    
    echo ''
    echo '🚀 Criando VM 753 para INSTALAÇÃO AUTOMÁTICA COMPLETA...'
    qm create 753 \
      --name 'pve753-auto-complete' \
      --memory 16384 \
      --cores 4 \
      --cpu host,flags=+pdpe1gb \
      --net0 virtio,bridge=vmbr0 \
      --scsi0 data02:100,cache=writethrough \
      --scsi1 data02:50,cache=writethrough \
      --ide2 local:iso/proxmox-minimal.iso,media=cdrom \
      --boot c \
      --bootdisk ide2 \
      --ostype l26 \
      --agent enabled=1

    echo '▶️ Iniciando VM 753 para instalação AUTOMÁTICA...'
    qm start 753

    echo ''
    echo '🎯 VM 753 CRIADA PARA INSTALAÇÃO AUTOMÁTICA COMPLETA!'
    echo ''
    echo '📊 Configurações:'
    echo '- Answer file MINIMAL (sem seções problemáticas)'
    echo '- disk_list = [\"sda\"] (sintaxe mais simples)'
    echo '- country = \"US\" (valor garantido)'
    echo '- DHCP automático'
    echo '- Root password: MpC2025!'
    echo ''
    echo '⏳ AGUARDE 15-20 MINUTOS para instalação completa'
    echo ''
    echo '🔍 TESTES DE VALIDAÇÃO:'
    echo '1. Aguarde instalação automática'
    echo '2. VM deve reiniciar automaticamente'
    echo '3. Teste SSH: ssh root@<IP_DA_VM>'
    echo '4. Acesse web: https://<IP_DA_VM>:8006'
    echo ''
    echo '✅ SE CONSEGUIR SSH = VALIDAÇÃO 100% COMPLETA!'
else
    echo '❌ Erro ao criar ISO - verificar sintaxe do answer file'
fi
"

echo ""
echo "🎯 VALIDAÇÃO AUTOMÁTICA INICIADA!"
echo ""
echo "✅ PRÓXIMOS PASSOS:"
echo "1. Aguarde 15-20 minutos para instalação completa"
echo "2. Monitore console da VM 753"
echo "3. Após instalação, VM deve reiniciar e ficar acessível"
echo "4. Teste SSH para confirmar sucesso total"
echo ""
echo "🏆 SUCESSO = SSH funcional + Web interface acessível"