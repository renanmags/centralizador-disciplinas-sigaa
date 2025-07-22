#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Iniciando o script de build final..."

# 1. Instala as dependências do Python
pip install -r requirements.txt

# 2. Instala o Google Chrome de forma manual, sem usar apt-get
echo "Baixando e extraindo o Google Chrome..."
wget -P /tmp https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x /tmp/google-chrome-stable_current_amd64.deb /tmp/chrome
rm /tmp/google-chrome-stable_current_amd64.deb

# 3. Move os arquivos do Chrome para uma pasta no projeto
mv /tmp/chrome/opt/google/chrome /opt/render/project/src/chrome

# 4. Adiciona a pasta do Chrome ao PATH do sistema
export PATH="${PATH}:/opt/render/project/src/chrome"

# 5. (A MÁGICA) Diz ao Chrome onde encontrar as bibliotecas do sistema que já existem na Render
# Isso evita a necessidade de instalar dependências com apt-get
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/render/project/src/chrome/lib"

echo "Build concluído com sucesso."