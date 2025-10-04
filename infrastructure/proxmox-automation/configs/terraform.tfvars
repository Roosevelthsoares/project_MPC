pm_api_url = "https://192.168.90.10:8006/api2/json"
pm_api_token_id = "terraform@pve!tofu-token"
pm_api_token = "7844a301-01ff-431d-ad1f-8afbbc0d315c"

# Variáveis de compatibilidade (não usadas)
pm_user = "terraform@pve"
pm_token = "7844a301-01ff-431d-ad1f-8afbbc0d315c"

# Configuração para automação completa
auto_create_nested_vms = true
nested_root_token = "automation-token-123"
nested_terraform_token = "terraform-automation-456"

# IPs e senhas (ajuste conforme necessário)
nested_api_host = "192.168.90.100"
pm_api_url_nested = "https://192.168.90.100:8006/api2/json"
pm_api_token_id_nested = "terraform@pve!automation"
pm_api_token_nested = "terraform-automation-456"

# Senhas (modifique para suas senhas desejadas)
nested_root_password = "root"
nested_terraform_password = "root"
securityonion_password = "root"
pfsense_password = "root"