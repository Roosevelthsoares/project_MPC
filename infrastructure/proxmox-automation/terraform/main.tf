terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "= 2.9.10"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

# Este arquivo funciona tanto com Terraform quanto com OpenTofu
# Use: tofu init, tofu plan, tofu apply

# Upload dos snippets de configuração (feito manualmente)
resource "null_resource" "upload_snippets" {
  provisioner "local-exec" {
    command = "echo 'Snippets já foram carregados manualmente'"
  }
}

provider "proxmox" {
  alias           = "labdef10"
  pm_api_url      = var.pm_api_url
  pm_api_token_id = var.pm_api_token_id
  pm_api_token_secret = var.pm_api_token
  pm_tls_insecure = true
}

provider "proxmox" {
  alias           = "nested"
  pm_api_url      = var.pm_api_url_nested
  pm_api_token_id = var.pm_api_token_id_nested
  pm_api_token_secret = var.pm_api_token_nested
  pm_tls_insecure = true
}

# VM 732 - Proxmox VE Nested (criação via API direta para evitar bugs do provider)
resource "null_resource" "create_vm_732" {
  depends_on = [null_resource.upload_snippets]
  
  provisioner "local-exec" {
    command = <<-EOT
      # Criar VM 732 via API direta
      curl -k -X POST \
        -H "Authorization: PVEAPIToken=${var.pm_api_token_id}=${var.pm_api_token}" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "vmid=732" \
        -d "name=PFC-MPC" \
        -d "memory=30518" \
        -d "cores=8" \
        -d "sockets=1" \
        -d "cpu=host" \
        -d "ostype=l26" \
        -d "numa=0" \
        -d "onboot=1" \
        -d "boot=order=scsi0;ide2;net0" \
        -d "scsihw=virtio-scsi-pci" \
        -d "scsi0=data02:228G" \
        -d "scsi1=data02:200G" \
        -d "ide2=local:iso/proxmox-ve-8.4-auto.iso,media=cdrom" \
        -d "net0=virtio,bridge=vmbr6001" \
        -d "net1=virtio,bridge=vmbr6003" \
        -d "ipconfig0=dhcp" \
        -d "ciuser=root" \
        -d "cipassword=root" \
        -d "cicustom=user=local:snippets/proxmox-autoinstall.yaml" \
        "${var.pm_api_url}/nodes/labdef10/qemu"
    EOT
  }
}

# Iniciar VM automaticamente após criação
resource "null_resource" "start_vm_732" {
  depends_on = [null_resource.create_vm_732]
  
  provisioner "local-exec" {
    command = <<-EOT
      curl -k -X POST \
        -H "Authorization: PVEAPIToken=${var.pm_api_token_id}=${var.pm_api_token}" \
        "${var.pm_api_url}/nodes/labdef10/qemu/732/status/start"
    EOT
  }
  
  triggers = {
    vm_id = "732"
  }
}

# Aguardar Proxmox nested ficar disponível
resource "null_resource" "wait_for_nested_proxmox" {
  depends_on = [null_resource.start_vm_732]
  
  provisioner "local-exec" {
    command = <<-EOT
      echo "Aguardando instalação automática do Proxmox completar..."
      echo "Isso pode levar 15-25 minutos..."
      
      max_attempts=90  # 45 minutos total
      attempt=1
      
      while [ $attempt -le $max_attempts ]; do
        echo "Tentativa $attempt/$max_attempts ($(date +%H:%M:%S))..."
        
        # Verificar se Proxmox API está respondendo
        if curl -s -k --connect-timeout 5 "https://192.168.90.100:8006/api2/json/version" >/dev/null 2>&1; then
          echo "Proxmox nested instalado e disponível!"
          
          # Aguardar mais um pouco para garantir que serviços estão estáveis
          echo "Aguardando serviços estabilizarem..."
          sleep 60
          exit 0
        fi
        
        echo "Instalação em progresso... aguardando 30 segundos..."
        sleep 30
        attempt=$((attempt + 1))
      done
      
      echo "Timeout: Instalação do Proxmox não completou em 45 minutos"
      exit 1
    EOT
  }
}

# Criar token API no Proxmox nested
resource "null_resource" "create_nested_token" {
  depends_on = [null_resource.wait_for_nested_proxmox]
  
  provisioner "local-exec" {
    command = <<-EOT
      # Aguardar um pouco mais para garantir que o Proxmox está completamente inicializado
      sleep 60
      
      # Criar usuário terraform no Proxmox nested
      curl -k -d "userid=terraform@pve" \
        -H "Authorization: PVEAPIToken=root@pam!${var.nested_root_token}" \
        "https://192.168.90.100:8006/api2/json/access/users" || true
      
      # Dar permissões de Administrator
      curl -k -d "path=/" -d "users=terraform@pve" -d "roles=Administrator" \
        -H "Authorization: PVEAPIToken=root@pam!${var.nested_root_token}" \
        "https://192.168.90.100:8006/api2/json/access/acl" || true
      
      # Criar token API
      curl -k -d "tokenid=automation" -d "privsep=0" \
        -H "Authorization: PVEAPIToken=root@pam!${var.nested_root_token}" \
        "https://192.168.90.100:8006/api2/json/access/users/terraform@pve/token/automation" || true
    EOT
  }
}

# VM 100 - Firewall (pfSense) - Configuração exata da VM 131
resource "null_resource" "create_pfsense_vm" {
  depends_on = [null_resource.create_nested_token]
  
  provisioner "local-exec" {
    command = <<-EOT
      # Criar VM 100 - Firewall (configuração exata da VM 131)
      curl -k -X POST \
        -H "Authorization: PVEAPIToken=terraform@pve!automation=${var.nested_terraform_token}" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "vmid=100" \
        -d "name=Firewall" \
        -d "memory=4096" \
        -d "cores=2" \
        -d "sockets=2" \
        -d "cpu=host" \
        -d "ostype=l26" \
        -d "numa=0" \
        -d "onboot=1" \
        -d "boot=order=scsi0;ide2;net0" \
        -d "scsihw=virtio-scsi-pci" \
        -d "scsi0=local-lvm:32G" \
        -d "ide2=cdrom,media=cdrom" \
        -d "net0=virtio,bridge=vmbr6001" \
        -d "net1=virtio,bridge=vmbr1" \
        -d "net2=virtio,bridge=vmbr5001" \
        -d "net3=virtio,bridge=vmbr6003" \
        -d "net4=virtio,bridge=vmbr6004" \
        -d "net5=virtio,bridge=vmbr1" \
        -d "net6=virtio,bridge=vmbr5002" \
        "https://192.168.90.100:8006/api2/json/nodes/pve/qemu"
      
      # Iniciar VM 100
      sleep 10
      curl -k -X POST \
        -H "Authorization: PVEAPIToken=terraform@pve!automation=${var.nested_terraform_token}" \
        "https://192.168.90.100:8006/api2/json/nodes/pve/qemu/100/status/start"
    EOT
  }
}

# VM 101 - Security Onion - Configuração exata da VM 131
resource "null_resource" "create_securityonion_vm" {
  depends_on = [null_resource.create_nested_token]
  
  provisioner "local-exec" {
    command = <<-EOT
      # Criar VM 101 - Security Onion (configuração exata da VM 131)
      curl -k -X POST \
        -H "Authorization: PVEAPIToken=terraform@pve!automation=${var.nested_terraform_token}" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "vmid=101" \
        -d "name=Security-Onion" \
        -d "memory=24576" \
        -d "cores=2" \
        -d "sockets=2" \
        -d "cpu=host" \
        -d "ostype=l26" \
        -d "numa=0" \
        -d "onboot=1" \
        -d "boot=order=scsi0;ide2;net0" \
        -d "scsihw=virtio-scsi-pci" \
        -d "scsi0=extra-lvm:224G" \
        -d "ide2=cdrom,media=cdrom" \
        -d "net0=virtio,bridge=vmbr5001" \
        -d "net1=virtio,bridge=vmbr1" \
        "https://192.168.90.100:8006/api2/json/nodes/pve/qemu"
      
      # Iniciar VM 101
      sleep 10
      curl -k -X POST \
        -H "Authorization: PVEAPIToken=terraform@pve!automation=${var.nested_terraform_token}" \
        "https://192.168.90.100:8006/api2/json/nodes/pve/qemu/101/status/start"
    EOT
  }
}