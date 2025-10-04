#!/bin/bash

# Implementação correta da instalação automatizada do Proxmox
# Seguindo exatamente a documentação oficial: https://pve.proxmox.com/wiki/Automated_Installation

echo "=== Instalação Automatizada Proxmox - Método Oficial ==="
echo ""

HOST="192.168.90.10"
VMID="732"
PASSWORD="MpC@2025$"

echo "1. Preparando ambiente no host Proxmox..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "
# Instalar ferramentas necessárias
apt update
apt install -y proxmox-auto-install-assistant xorriso wget

# Criar diretório de trabalho
mkdir -p /tmp/proxmox-auto-install
cd /tmp/proxmox-auto-install
"

echo "2. Baixando ISO original do Proxmox (se necessário)..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "
cd /tmp/proxmox-auto-install

# Verificar se já temos o ISO
if [ ! -f /var/lib/vz/template/iso/proxmox-ve_8.4-1.iso ]; then
    echo 'ISO não encontrado localmente'
    exit 1
fi

# Copiar ISO para diretório de trabalho
cp /var/lib/vz/template/iso/proxmox-ve_8.4-1.iso ./proxmox-ve_8.4-1.iso
"

echo "3. Criando answer file oficial..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "
cd /tmp/proxmox-auto-install

cat > answer.toml << 'EOF'
[global]
keyboard = \"en-us\"
country = \"br\"
fqdn = \"proxmox-mpc.local\"
mailto = \"admin@localhost\"
timezone = \"America/Sao_Paulo\"
root-password = \"MpC2025\"

[network]
source = \"from-dhcp\"

[disk-setup]
filesystem = \"ext4\"
disk-list = [\"sda\"]
EOF
"

echo "4. Validando answer file..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "
cd /tmp/proxmox-auto-install
proxmox-auto-install-assistant validate-answer answer.toml
"

echo "5. Preparando ISO automatizado..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "
cd /tmp/proxmox-auto-install

# Preparar ISO com answer file incluído
proxmox-auto-install-assistant prepare-iso ./proxmox-ve_8.4-1.iso \
    --fetch-from iso \
    --answer-file ./answer.toml \
    --output ./proxmox-ve_8.4-1-auto.iso

# Verificar se ISO foi criado
ls -la proxmox-ve_8.4-1-auto.iso
"

echo "6. Copiando ISO automatizado para storage..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "
cd /tmp/proxmox-auto-install
cp ./proxmox-ve_8.4-1-auto.iso /var/lib/vz/template/iso/
"

echo "7. Parando VM atual e reconfigurando..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "
qm stop $VMID 2>/dev/null || true
sleep 3

# Reconfigurar VM para usar ISO automatizado
qm set $VMID --ide2 local:iso/proxmox-ve_8.4-1-auto.iso,media=cdrom
qm set $VMID --boot order=ide2;scsi0
"

echo "8. Iniciando VM com instalação automatizada..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST "qm start $VMID"

echo ""
echo "✅ INSTALAÇÃO AUTOMATIZADA INICIADA!"
echo ""
echo "📋 CONFIGURAÇÃO APLICADA:"
echo "   🔧 Answer file validado"
echo "   💿 ISO automatizado criado: proxmox-ve_8.4-1-auto.iso"
echo "   🖥️  VM configurada para boot automático"
echo "   🔑 Senha root: MpC2025"
echo "   🌐 Rede: DHCP automático"
echo ""
echo "⏰ PROCESSO AUTOMÁTICO:"
echo "   1. Boot automático após 10 segundos"
echo "   2. Instalação completamente não-interativa"
echo "   3. Reinício automático após instalação"
echo "   4. Sistema pronto para uso"
echo ""
echo "🔍 MONITORAMENTO:"
echo "   - Via console web: instalação deve prosseguir sozinha"
echo "   - Tempo estimado: 10-15 minutos"
echo "   - Login final: root / MpC2025"
echo ""
echo "📝 LOGS DE TROUBLESHOOTING (na VM após instalação):"
echo "   - /tmp/fetch_answer.log"
echo "   - /tmp/auto_installer"
echo "   - /tmp/install-low-level-start-session.log"