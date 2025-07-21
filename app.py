from flask import Flask, render_template, request, session, url_for, redirect
# (ALTERADO) A importação agora aponta para o novo pacote 'scraper'
from scraper import get_sigaa_disciplinas
import os

app = Flask(__name__)
# É uma boa prática usar uma chave secreta para a sessão
app.secret_key = os.urandom(24) 

@app.route('/')
def index():
    # Limpa a sessão antiga para garantir uma página de login limpa
    session.clear()
    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Protege a rota: só permite acesso se o usuário estiver logado (verificado pela sessão)
    if 'nome_aluno' in session and session['nome_aluno']:
        return render_template('dashboard.html')
    else:
        # Se não estiver logado, redireciona para a página de login
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def processar_login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    if not usuario or not senha:
        session['erro'] = 'Usuário e senha são obrigatórios.'
        return redirect(url_for('index'))

    print(f"Recebido pedido para o utilizador: {usuario}. A chamar o scraper...")
    
    # Chama a função do scraper, que agora está organizada no pacote
    dados_sigaa = get_sigaa_disciplinas(usuario, senha)
    
    # Verifica se o scraper retornou dados válidos (um nome de aluno é um bom indicador)
    if not dados_sigaa or not dados_sigaa.get("nome_aluno"):
        session['erro'] = 'Login falhou. Verifique as suas credenciais e tente novamente.'
        # Limpa qualquer dado parcial que possa ter sido salvo
        session.clear()
        return redirect(url_for('index'))
    else:
        # Limpa qualquer mensagem de erro anterior e preenche a sessão com os dados do usuário
        session.pop('erro', None)
        session['nome_aluno'] = dados_sigaa.get('nome_aluno', 'Aluno')
        session['nome_curso'] = dados_sigaa.get('nome_curso', 'Curso Desconhecido')
        session['disciplinas'] = dados_sigaa.get('disciplinas', [])
        session['atividades'] = dados_sigaa.get('atividades', [])
        
        return redirect(url_for('dashboard'))

# Rota para fazer logout e limpar a sessão
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
