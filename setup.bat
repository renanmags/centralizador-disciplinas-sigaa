@echo off
python -m venv env
call env\Scripts\activate
pip install -r requirements.txt
echo Dependências instaladas com sucesso! Ative o ambiente com: env\Scripts\activate
pause