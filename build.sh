#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Iniciando o script de build..."

# Instala as dependências do Python
pip install -r requirements.txt

# --- LÓGICA DE INSTALAÇÃO DO CHROME ATUALIZADA ---
echo "Configurando repositório do Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'

echo "Atualizando lista de pacotes e instalando dependências..."
apt-get update

# Instala o Chrome e suas dependências essenciais
echo "Instalando o Google Chrome e dependências..."
apt-get install -y google-chrome-stable libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1

echo "Build concluído com sucesso."