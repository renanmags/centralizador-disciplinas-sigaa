#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Iniciando o script de build..."

# Instala as dependências do Python
pip install -r requirements.txt

# Instala o Google Chrome de forma manual, sem precisar de 'sudo'
echo "Instalando o Google Chrome..."
wget -P /tmp https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x /tmp/google-chrome-stable_current_amd64.deb /tmp/chrome
rm /tmp/google-chrome-stable_current_amd64.deb

# Move os arquivos do Chrome para uma pasta que persiste após o build
# O Selenium Manager irá encontrar o executável do Chrome aqui.
mv /tmp/chrome/opt/google/chrome /opt/render/project/src/chrome
# Adiciona a pasta do Chrome ao PATH do sistema
export PATH="${PATH}:/opt/render/project/src/chrome"

echo "Build concluído com sucesso."