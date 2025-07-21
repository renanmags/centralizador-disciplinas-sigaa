from flask import Flask, render_template, request, session, url_for, redirect, jsonify
from scraper import get_sigaa_disciplinas
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

@app.route('/')
def index():
    if 'nome_aluno' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'nome_aluno' in session and session['nome_aluno']:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def processar_login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    if not usuario or not senha:
        session['erro'] = 'Usuário e senha são obrigatórios.'
        return jsonify({'status': 'error', 'message': 'Campos obrigatórios'})

    dados_sigaa = get_sigaa_disciplinas(usuario, senha, browser="auto")
    
    if not dados_sigaa or not dados_sigaa.get("nome_aluno"):
        session['erro'] = 'Login falhou. Verifique suas credenciais e tente novamente.'
        return jsonify({'status': 'error', 'message': 'Login inválido'})
    else:
        session.pop('erro', None)
        session['nome_aluno'] = dados_sigaa.get('nome_aluno', 'Aluno')
        session['nome_curso'] = dados_sigaa.get('nome_curso', 'Curso Desconhecido')
        session['disciplinas'] = dados_sigaa.get('disciplinas', [])
        session['atividades'] = dados_sigaa.get('atividades', [])
        
        # Em vez de redirecionar, envia uma resposta de sucesso para o JavaScript
        return jsonify({'status': 'success', 'redirect_url': url_for('dashboard')})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)