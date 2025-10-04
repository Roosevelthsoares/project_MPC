#!/bin/bash

echo "🔧 CRIANDO ANSWER FILE COM SSH HABILITADO"
echo "=== Answer file que habilita SSH durante instalação ==="

# Criar answer file melhorado que habilita SSH
sshpass -p "MpC@2025$" ssh -o StrictHostKeyChecking=no root@192.168.90.10 "
cat > /tmp/answer_ssh_enabled.toml << 'EOF'
[global]
keyboard = \"en-us\"
country = \"US\"
fqdn = \"pve750-validation.local\"
mailto = \"admin@local\"
timezone = \"America/Sao_Paulo\"
root_password = \"MpC2025!\"

[network]
source = \"static\"
cidr = \"192.168.90.30/24\"
dns = \"192.168.90.1\"
gateway = \"192.168.90.1\"

[disk-setup]
filesystem = \"ext4\"
disk_list = [\"scsi0\"]

[post-install-script]
script = '''#!/bin/bash
echo \"🔧 Configurando SSH durante instalação...\"

# Habilitar SSH
systemctl enable ssh
systemctl start ssh

# Permitir login root via SSH
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Reiniciar SSH
systemctl restart ssh

# Configurar interfaces de rede adicionais
cat > /etc/systemd/network/30-vmbr6001.network << NETEOF
[Match]
Name=ens19

[Network]
DHCP=no
NETEOF

cat > /etc/systemd/network/31-vmbr6003.network << NETEOF
[Match]
Name=ens20

[Network]
DHCP=no
NETEOF

systemctl restart systemd-networkd

# Log de conclusão
echo \"✅ SSH configurado e habilitado\" >> /var/log/proxmox-install.log
echo \"✅ Interfaces configuradas\" >> /var/log/proxmox-install.log
'''
EOF

echo '✅ Answer file com SSH criado em /tmp/answer_ssh_enabled.toml'
"

echo ""
echo "🚀 Criando ISO automatizada com SSH habilitado..."
sshpass -p "MpC@2025$" ssh -o StrictHostKeyChecking=no root@192.168.90.10 "
# Criar nova ISO com answer file que habilita SSH
proxmox-auto-install-assistant prepare-iso \
  /var/lib/vz/template/iso/proxmox-ve_8.4-1.iso \
  --answer-file /tmp/answer_ssh_enabled.toml \
  --out /var/lib/vz/template/iso/proxmox-ssh-enabled.iso

echo '✅ ISO com SSH habilitado criada!'
ls -la /var/lib/vz/template/iso/proxmox-ssh-enabled.iso
"