#!/bin/bash

# Script para automatizar a instalação do Proxmox na VM 732
# Simula as teclas necessárias para completar a instalação

echo "=== Automatizando Instalação do Proxmox na VM 732 ==="
echo ""

HOST="192.168.90.10"
VMID="732"
PASSWORD="MpC@2025$"

# Função para enviar tecla
send_key() {
    local key="$1"
    local description="$2"
    echo "🔘 Enviando: $description ($key)"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$HOST \
        "echo 'sendkey $key' | qm monitor $VMID" > /dev/null 2>&1
    sleep 2
}

# Função para enviar texto
send_text() {
    local text="$1"
    local description="$2"
    echo "✏️  Digitando: $description"
    for (( i=0; i<${#text}; i++ )); do
        char="${text:$i:1}"
        case "$char" in
            " ") send_key "spc" "espaço" ;;
            ".") send_key "dot" "ponto" ;;
            "@") send_key "shift-2" "@" ;;
            "2") send_key "2" "2" ;;
            "0") send_key "0" "0" ;;
            "5") send_key "5" "5" ;;
            "$") send_key "shift-4" "$" ;;
            *) send_key "$char" "$char" ;;
        esac
        sleep 0.5
    done
}

echo "🚀 Iniciando automação da instalação..."
sleep 3

# 1. Pressionar Enter para iniciar instalação (caso ainda não tenha iniciado)
send_key "ret" "Enter para iniciar instalação"
sleep 5

# 2. Aceitar licença (geralmente Enter ou 'I Agree')
send_key "ret" "Aceitar licença"
sleep 3

# 3. Selecionar disco (geralmente já está selecionado)
send_key "ret" "Confirmar seleção de disco"
sleep 3

# 4. Configuração de país/timezone (usar padrão)
send_key "ret" "Confirmar timezone"
sleep 3

# 5. Configurar senha root
echo "🔑 Configurando senha root..."
send_text "MpC2025" "senha root"
send_key "tab" "próximo campo"
send_text "MpC2025" "confirmar senha"
send_key "ret" "confirmar senhas"
sleep 3

# 6. Configurar email (usar padrão ou pular)
send_key "tab" "campo email"
send_text "admin@localhost" "email"
send_key "ret" "confirmar email"
sleep 3

# 7. Configuração de rede (usar padrão)
send_key "ret" "confirmar configuração de rede"
sleep 5

# 8. Iniciar instalação
send_key "ret" "iniciar instalação"

echo ""
echo "✅ Automação iniciada!"
echo "🕐 A instalação pode levar 10-15 minutos"
echo "📺 Monitore o progresso via console da interface web"
echo ""
echo "🔑 Credenciais configuradas:"
echo "   👤 Usuário: root"
echo "   🔑 Senha: MpC2025"
echo ""
echo "⏰ Aguarde a instalação terminar e depois:"
echo "   1. A VM vai reiniciar automaticamente"
echo "   2. Acesse via: https://[IP-da-VM]:8006"
echo "   3. Login com as credenciais acima"