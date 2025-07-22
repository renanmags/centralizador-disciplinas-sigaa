#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Iniciando o script de build final..."

# 1. Instala as dependências do Python
pip install -r requirements.txt

# 2. Atualiza os pacotes do sistema e instala as dependências do Chrome
echo "Instalando dependências de sistema para o Google Chrome..."
apt-get update
apt-get install -y wget gnupg libnss3 libgconf-2-4 libgdk-pixbuf2.0-0 libgtk-3-0 libxss1 libasound2 libgbm1

# 3. Instala o Google Chrome de forma manual
echo "Baixando e extraindo o Google Chrome..."
wget -P /tmp https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x /tmp/google-chrome-stable_current_amd64.deb /tmp/chrome
rm /tmp/google-chrome-stable_current_amd64.deb

# 4. Move os arquivos do Chrome para o local correto
mv /tmp/chrome/opt/google/chrome /opt/render/project/src/chrome
export PATH="${PATH}:/opt/render/project/src/chrome"

echo "Build concluído com sucesso."