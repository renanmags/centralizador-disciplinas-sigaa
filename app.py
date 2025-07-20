from flask import Flask, render_template, request, session, url_for, redirect
from scraper_module import get_sigaa_disciplinas
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

@app.route('/')
def index():
    """
    Rota principal que exibe a página de login.
    """
    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Esta rota exibe o dashboard se o utilizador já estiver logado (dados na sessão).
    """
    # Verifica se os dados do utilizador já existem na sessão
    if 'nome_aluno' in session and session['nome_aluno']:
        return render_template('dashboard.html')
    else:
        # Se não, manda o utilizador de volta para a página de login
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def processar_login():
    """
    Esta rota recebe os dados do formulário, chama o scraper e redireciona para o dashboard.
    """
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    if not usuario or not senha:
        session['erro'] = 'Usuário e senha são obrigatórios.'
        return redirect(url_for('index'))

    print(f"Recebido pedido para o utilizador: {usuario}. A chamar o scraper...")
    
    dados_sigaa = get_sigaa_disciplinas(usuario, senha)
    
    # Verifica se o scraper conseguiu extrair o nome do aluno como sinal de sucesso
    if not dados_sigaa or not dados_sigaa.get("nome_aluno"):
        session['erro'] = 'Login falhou. Verifique as suas credenciais e tente novamente.'
        session.clear()
        return redirect(url_for('index'))
    else:
        # Se o login for bem-sucedido, guarda os dados na sessão
        session.pop('erro', None)
        session['nome_aluno'] = dados_sigaa.get('nome_aluno', 'Aluno')
        session['nome_curso'] = dados_sigaa.get('nome_curso', 'Curso Desconhecido')
        session['disciplinas'] = dados_sigaa.get('disciplinas', [])
        # Redireciona para a rota GET do dashboard, que irá exibir os dados
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
