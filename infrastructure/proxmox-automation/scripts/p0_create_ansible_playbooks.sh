#!/bin/bash

# 🤖 P0-4: Criação de Ansible Playbooks
# Automatizar configuração pós-instalação das VMs
# Data: 28 de setembro de 2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🤖 P0-4: CRIAÇÃO DE ANSIBLE PLAYBOOKS${NC}"
echo "===================================="
echo ""

ANSIBLE_DIR="../ansible"
PLAYBOOKS_DIR="$ANSIBLE_DIR/playbooks"
ROLES_DIR="$ANSIBLE_DIR/roles"
INVENTORY_FILE="$ANSIBLE_DIR/inventory.yml"

echo -e "${YELLOW}📋 ESTRUTURA ANSIBLE A SER CRIADA:${NC}"
echo "================================="
echo "📁 ansible/"
echo "├── inventory.yml           # Inventário de hosts"
echo "├── ansible.cfg            # Configuração Ansible"
echo "├── playbooks/            # Playbooks principais"
echo "│   ├── site.yml          # Playbook principal"
echo "│   ├── proxmox-setup.yml # Setup hosts Proxmox"
echo "│   ├── pfsense-config.yml # Configuração pfSense"
echo "│   └── security-onion-config.yml # Config Security Onion"
echo "└── roles/               # Roles reutilizáveis"
echo "    ├── common/          # Configurações comuns"
echo "    ├── proxmox/         # Role Proxmox"
echo "    ├── pfsense/         # Role pfSense"
echo "    └── security-onion/  # Role Security Onion"
echo ""

read -p "Criar estrutura Ansible completa? (s/N): " confirm
if [[ $confirm != "s" && $confirm != "S" ]]; then
    echo "❌ Operação cancelada"
    exit 1
fi

echo -e "${GREEN}🚀 CRIANDO ESTRUTURA ANSIBLE...${NC}"

# Criar diretórios
mkdir -p $ANSIBLE_DIR $PLAYBOOKS_DIR $ROLES_DIR
mkdir -p $ROLES_DIR/{common,proxmox,pfsense,security-onion}/{tasks,handlers,templates,vars,defaults}

echo -e "${GREEN}✅ Diretórios criados${NC}"

# 1. Criar ansible.cfg
echo -e "${YELLOW}⚙️ Criando ansible.cfg...${NC}"
cat > $ANSIBLE_DIR/ansible.cfg << 'EOF'
[defaults]
inventory = inventory.yml
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = memory
stdout_callback = yaml
bin_ansible_callbacks = True

[ssh_connection]
ssh_args = -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
EOF

# 2. Criar inventário
echo -e "${YELLOW}📋 Criando inventory.yml...${NC}"
cat > $INVENTORY_FILE << 'EOF'
all:
  children:
    proxmox_hosts:
      hosts:
        pve732:
          ansible_host: 192.168.90.20
          ansible_user: root
          ansible_ssh_pass: "MpC2025!"
        pve754:
          ansible_host: 192.168.91.101
          ansible_user: root
          ansible_ssh_pass: "MpC2025!"
    
    firewalls:
      hosts:
        pfsense-vm100:
          ansible_host: "{{ pfsense_lan_ip | default('192.168.1.1') }}"
          ansible_user: admin
          ansible_connection: httpapi
          ansible_httpapi_use_ssl: true
          ansible_httpapi_validate_certs: false
    
    ids_systems:
      hosts:
        security-onion-vm101:
          ansible_host: "{{ so_management_ip | default('192.168.90.101') }}"
          ansible_user: souser
          ansible_ssh_pass: "{{ so_password }}"

  vars:
    # Credenciais globais
    proxmox_api_user: "terraform@pve"
    proxmox_api_token: "7844a301-01ff-431d-ad1f-8afbbc0d315c"
    
    # Configurações de rede
    management_network: "192.168.90.0/24"
    internal_network: "192.168.91.0/24"
EOF

# 3. Criar playbook principal
echo -e "${YELLOW}📜 Criando site.yml...${NC}"
cat > $PLAYBOOKS_DIR/site.yml << 'EOF'
---
# Site.yml - Playbook principal MPC 1.0
# Configura toda a infraestrutura de segurança

- name: "Configurar hosts Proxmox"
  import_playbook: proxmox-setup.yml

- name: "Configurar pfSense Firewalls"
  import_playbook: pfsense-config.yml

- name: "Configurar Security Onion IDS"
  import_playbook: security-onion-config.yml
EOF

# 4. Playbook Proxmox
echo -e "${YELLOW}🏗️ Criando proxmox-setup.yml...${NC}"
cat > $PLAYBOOKS_DIR/proxmox-setup.yml << 'EOF'
---
- name: "Setup Proxmox VE Hosts"
  hosts: proxmox_hosts
  become: yes
  gather_facts: yes
  
  roles:
    - common
    - proxmox

  tasks:
    - name: "Atualizar sistema"
      apt:
        update_cache: yes
        upgrade: dist
        
    - name: "Configurar NTP"
      systemd:
        name: ntp
        enabled: yes
        state: started
        
    - name: "Configurar bridges de rede"
      template:
        src: interfaces.j2
        dest: /etc/network/interfaces
        backup: yes
      notify: restart networking
        
    - name: "Verificar status das VMs"
      shell: "qm list"
      register: vm_status
      
    - name: "Mostrar VMs existentes"
      debug:
        var: vm_status.stdout_lines
EOF

# 5. Playbook pfSense
echo -e "${YELLOW}🔥 Criando pfsense-config.yml...${NC}"
cat > $PLAYBOOKS_DIR/pfsense-config.yml << 'EOF'
---
- name: "Configurar pfSense Firewall"
  hosts: firewalls
  gather_facts: no
  
  vars:
    pfsense_interfaces:
      - name: "WAN"
        interface: "vtnet1"
        type: "dhcp"
      - name: "LAN"
        interface: "vtnet2"  
        ip: "192.168.1.1"
        subnet: "24"
    
    pfsense_rules:
      - action: "pass"
        interface: "LAN"
        source: "LAN net"
        destination: "any"
        description: "Allow LAN to any"

  tasks:
    - name: "Aguardar pfSense ficar disponível"
      wait_for:
        host: "{{ ansible_host }}"
        port: 443
        timeout: 300
        
    - name: "Configurar interfaces pfSense"
      debug:
        msg: "Configuração pfSense via API será implementada"
        
    # TODO: Implementar módulos pfSense específicos
    # - pfsense_interface:
    #     name: "{{ item.name }}"
    #     interface: "{{ item.interface }}"
    #     type: "{{ item.type }}"
    #   loop: "{{ pfsense_interfaces }}"
EOF

# 6. Playbook Security Onion
echo -e "${YELLOW}🛡️ Criando security-onion-config.yml...${NC}"
cat > $PLAYBOOKS_DIR/security-onion-config.yml << 'EOF'
---
- name: "Configurar Security Onion IDS"
  hosts: ids_systems
  become: yes
  gather_facts: yes
  
  vars:
    so_interface_management: "ens3"
    so_interface_monitor: "ens4"
    so_rules_update: true
    
  tasks:
    - name: "Aguardar Security Onion ficar disponível"
      wait_for_connection:
        timeout: 300
        
    - name: "Verificar status dos serviços SO"
      systemctl:
        name: "{{ item }}"
        state: started
      loop:
        - suricata
        - zeek
        - elasticsearch
      ignore_errors: yes
      
    - name: "Atualizar regras Suricata"
      shell: "so-rule-update"
      when: so_rules_update
      
    - name: "Configurar interface de monitoramento"
      lineinfile:
        path: /opt/so/saltstack/salt/common/tools/sbin/so-interface
        regexp: '^MONITOR_INTERFACE='
        line: "MONITOR_INTERFACE={{ so_interface_monitor }}"
      notify: restart suricata
      
  handlers:
    - name: restart suricata  
      systemctl:
        name: suricata
        state: restarted
EOF

# 7. Role comum
echo -e "${YELLOW}🔧 Criando role common...${NC}"
cat > $ROLES_DIR/common/tasks/main.yml << 'EOF'
---
- name: "Instalar pacotes básicos"
  package:
    name:
      - vim
      - htop
      - curl
      - wget
      - net-tools
      - tcpdump
    state: present

- name: "Configurar timezone"
  timezone:
    name: "America/Sao_Paulo"

- name: "Configurar SSH"
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: "^#?PermitRootLogin"
    line: "PermitRootLogin yes"
  notify: restart ssh

- name: "Criar usuário MPC"
  user:
    name: mpc
    groups: sudo
    shell: /bin/bash
    create_home: yes
EOF

cat > $ROLES_DIR/common/handlers/main.yml << 'EOF'
---
- name: restart ssh
  systemctl:
    name: sshd
    state: restarted

- name: restart networking
  systemctl:
    name: networking
    state: restarted
EOF

# 8. Role Proxmox
echo -e "${YELLOW}🏗️ Criando role proxmox...${NC}"
cat > $ROLES_DIR/proxmox/tasks/main.yml << 'EOF'
---
- name: "Configurar repositórios Proxmox"
  apt_repository:
    repo: "deb http://download.proxmox.com/debian/pve {{ ansible_distribution_release }} pve-no-subscription"
    state: present
    
- name: "Atualizar cache apt"
  apt:
    update_cache: yes
    
- name: "Verificar serviços Proxmox"
  systemctl:
    name: "{{ item }}"
    state: started
    enabled: yes
  loop:
    - pvedaemon
    - pveproxy
    - pvestatd
    
- name: "Configurar firewall Proxmox"
  shell: "pve-firewall start"
  ignore_errors: yes
EOF

# 9. Script de execução
echo -e "${YELLOW}🚀 Criando script de execução...${NC}"
cat > $ANSIBLE_DIR/run-playbooks.sh << 'EOF'
#!/bin/bash

# Script para executar playbooks Ansible - MPC 1.0

set -e

cd "$(dirname "$0")"

echo "🤖 EXECUTANDO ANSIBLE PLAYBOOKS - MPC 1.0"
echo "========================================"

# Verificar se ansible está instalado
if ! command -v ansible &> /dev/null; then
    echo "❌ Ansible não está instalado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y ansible
fi

echo "✅ Ansible encontrado: $(ansible --version | head -n1)"

# Menu de opções
echo ""
echo "📋 PLAYBOOKS DISPONÍVEIS:"
echo "========================"
echo "1. Executar todos (site.yml)"
echo "2. Apenas Proxmox (proxmox-setup.yml)"
echo "3. Apenas pfSense (pfsense-config.yml)"
echo "4. Apenas Security Onion (security-onion-config.yml)"
echo "5. Verificar conectividade"
echo ""

read -p "Escolha uma opção (1-5): " choice

case $choice in
    1)
        echo "🚀 Executando todos os playbooks..."
        ansible-playbook playbooks/site.yml -v
        ;;
    2)
        echo "🏗️ Executando setup Proxmox..."
        ansible-playbook playbooks/proxmox-setup.yml -v
        ;;
    3)
        echo "🔥 Executando configuração pfSense..."
        ansible-playbook playbooks/pfsense-config.yml -v
        ;;
    4)
        echo "🛡️ Executando configuração Security Onion..."
        ansible-playbook playbooks/security-onion-config.yml -v
        ;;
    5)
        echo "🔍 Verificando conectividade..."
        ansible all -m ping
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ EXECUÇÃO CONCLUÍDA!"
EOF

chmod +x $ANSIBLE_DIR/run-playbooks.sh

echo ""
echo -e "${GREEN}🎉 ESTRUTURA ANSIBLE CRIADA COM SUCESSO!${NC}"
echo "========================================"
echo ""
echo -e "${BLUE}📁 ESTRUTURA CRIADA:${NC}"
echo "─────────────────"
find $ANSIBLE_DIR -type f | sort

echo ""
echo -e "${BLUE}🚀 COMO USAR:${NC}"
echo "──────────"
echo "1. Editar inventário: $INVENTORY_FILE"
echo "2. Personalizar playbooks em: $PLAYBOOKS_DIR/"
echo "3. Executar: cd $ANSIBLE_DIR && ./run-playbooks.sh"
echo ""
echo -e "${YELLOW}📋 PRÓXIMOS PASSOS:${NC}"
echo "─────────────────"
echo "• Configurar credenciais específicas no inventário"
echo "• Testar conectividade: ansible all -m ping"
echo "• Executar configuração: ./run-playbooks.sh"
echo "• Personalizar roles conforme necessário"

# Salvar log
echo "$(date): Estrutura Ansible criada com playbooks e roles" >> /tmp/mpc_config.log

echo ""
echo -e "${GREEN}✅ SCRIPT P0-4 CONCLUÍDO!${NC}"