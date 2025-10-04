variable "pm_api_url" {
  description = "URL da API do Proxmox labdef10"
  type        = string
  default     = "https://192.168.90.10:8006/api2/json"
}

variable "pm_api_token_id" {
  description = "ID do token API do Proxmox labdef10 (terraform@pve!tofu-token)"
  type        = string
}

variable "pm_api_token" {
  description = "Secret do token API do Proxmox labdef10"
  type        = string
  sensitive   = true
}

# Nested Proxmox (VM 731)
variable "nested_api_host" {
  description = "IP/hostname do Proxmox nested após boot"
  type        = string
}

variable "nested_root_password" {
  description = "Senha do root do Proxmox nested (definida pelo ISO auto)"
  type        = string
  sensitive   = true
}

variable "nested_terraform_password" {
  description = "Senha para o usuário terraform@pve no Proxmox nested"
  type        = string
  sensitive   = true
}

# Provider nested (após configuração da VM 731)
variable "pm_api_url_nested" {
  description = "URL da API do Proxmox nested"
  type        = string
}

variable "pm_api_token_id_nested" {
  description = "ID do token API no Proxmox nested (terraform@pve!tofu-token)"
  type        = string
}

variable "pm_api_token_nested" {
  description = "Secret do token API no Proxmox nested"
  type        = string
  sensitive   = true
}

# Flags de controle
variable "create_nested_vms" {
  description = "Se true, cria as VMs 100 e 101 no nested"
  type        = bool
  default     = false
}

variable "configure_pfsense" {
  description = "Se true, tenta configurar o pfSense via SSH/XML"
  type        = bool
  default     = false
}

# Credenciais para pós-instalação
variable "securityonion_ip" {
  description = "IP do Security Onion após instalação"
  type        = string
  default     = "10.10.10.101"
}

variable "securityonion_password" {
  description = "Senha do root do Security Onion"
  type        = string
  sensitive   = true
}

variable "pfsense_ip" {
  description = "IP do pfSense após instalação básica"
  type        = string
  default     = "10.10.10.100"
}

variable "pfsense_password" {
  description = "Senha do admin do pfSense"
  type        = string
  sensitive   = true
}

# Novas variáveis para automação completa
variable "nested_root_token" {
  description = "Token do root no Proxmox nested (gerado automaticamente)"
  type        = string
  sensitive   = true
  default     = "automation-token-123"
}

variable "nested_terraform_token" {
  description = "Token do terraform no Proxmox nested (gerado automaticamente)" 
  type        = string
  sensitive   = true
  default     = "terraform-automation-456"
}

variable "auto_create_nested_vms" {
  description = "Se true, cria automaticamente VMs 100 e 101 após VM 731 ficar pronta"
  type        = bool
  default     = true
}

# Variáveis para compatibilidade com terraform.tfvars
variable "pm_user" {
  description = "Usuário do Proxmox (compatibilidade)"
  type        = string
  default     = ""
}

variable "pm_token" {
  description = "Token do Proxmox (compatibilidade)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "pm_password" {
  description = "Senha do Proxmox (compatibilidade)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "enable_nested_automation" {
  description = "Habilitar automação completa incluindo instalação do Proxmox"
  type        = bool
  default     = true
}

variable "enable_nested_vm_creation" {
  description = "Habilitar criação automática das VMs 100 e 101"
  type        = bool
  default     = true
}
