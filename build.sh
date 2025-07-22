#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Iniciando o script de build..."

# Instala as dependências do Python
pip install -r requirements.txt

# --- LÓGICA DE INSTALAÇÃO DO CHROME ATUALIZADA ---
# Remove avisos do apt
export DEBIAN_FRONTEND=noninteractive

echo "Atualizando lista de pacotes e instalando dependências base..."
# Usamos 'sudo' aqui, que é permitido pela Render para o apt-get
sudo apt-get update
# Instala pacotes necessários para baixar e adicionar chaves de repositório
sudo apt-get install -y wget gnupg

echo "Baixando e adicionando a chave do Google Chrome..."
# Baixa a chave para uma pasta temporária onde temos permissão de escrita
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg

echo "Configurando o repositório do Google Chrome..."
# Adiciona o repositório do Chrome à lista de fontes do sistema
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'

echo "Atualizando a lista de pacotes novamente..."
sudo apt-get update

# Instala o Chrome e suas dependências essenciais
echo "Instalando o Google Chrome..."
sudo apt-get install -y google-chrome-stable

echo "Build concluído com sucesso."