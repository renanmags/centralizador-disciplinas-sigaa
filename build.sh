#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Iniciando o script de build final..."

# Instala as dependências do Python
pip install -r requirements.txt

# Instala o Google Chrome de forma manual, sem precisar de 'sudo' ou 'apt'
echo "Baixando e extraindo o Google Chrome..."
wget -P /tmp https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x /tmp/google-chrome-stable_current_amd64.deb /tmp/chrome
rm /tmp/google-chrome-stable_current_amd64.deb

# Move os arquivos do Chrome para uma pasta no projeto
# O Selenium Manager irá encontrar o executável do Chrome aqui.
mv /tmp/chrome/opt/google/chrome /opt/render/project/src/chrome

# Adiciona a pasta do Chrome ao PATH do sistema para que o Selenium o encontre
export PATH="${PATH}:/opt/render/project/src/chrome"

echo "Build concluído com sucesso."