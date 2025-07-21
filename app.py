from flask import Flask, render_template, request, session, url_for, redirect
from scraper_module import get_sigaa_disciplinas
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

@app.route('/')
def index():
    session.clear()
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
        return redirect(url_for('index'))

    print(f"Recebido pedido para o utilizador: {usuario}. A chamar o scraper...")
    
    dados_sigaa = get_sigaa_disciplinas(usuario, senha)
    
    if not dados_sigaa or not dados_sigaa.get("nome_aluno"):
        session['erro'] = 'Login falhou. Verifique as suas credenciais e tente novamente.'
        session.clear()
        return redirect(url_for('index'))
    else:
        session.pop('erro', None)
        session['nome_aluno'] = dados_sigaa.get('nome_aluno', 'Aluno')
        session['nome_curso'] = dados_sigaa.get('nome_curso', 'Curso Desconhecido')
        session['disciplinas'] = dados_sigaa.get('disciplinas', [])
        # --- CORREÇÃO APLICADA AQUI ---
        # Agora também guardamos a lista de atividades na sessão
        session['atividades'] = dados_sigaa.get('atividades', [])
        
        return redirect(url_for('dashboard'))

# --- NOVA ROTA ADICIONADA ---
# Rota para fazer logout e limpar a sessão
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
