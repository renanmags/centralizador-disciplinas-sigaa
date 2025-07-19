from flask import Flask, render_template, request, session, url_for, redirect
# Importamos a função com o nome que você pediu
from scraper_module import get_sigaa_disciplinas
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

@app.route('/')
def index():
    session.clear()
    return render_template('login.html')

# --- CORREÇÃO APLICADA AQUI ---
# A rota agora é '/dashboard' para corresponder ao 'action' do formulário HTML
@app.route('/dashboard', methods=['POST'])
def buscar_dados():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    if not usuario or not senha:
        session['erro'] = 'Usuário e senha são obrigatórios.'
        return redirect(url_for('index'))

    print(f"Recebido pedido para o utilizador: {usuario}. A chamar o scraper...")
    
    # Chamamos a função do scraper, que retorna um dicionário
    dados_sigaa = get_sigaa_disciplinas(usuario, senha)
    
    # Verificamos se o scraper conseguiu extrair o nome do aluno como sinal de sucesso
    if not dados_sigaa or not dados_sigaa.get("nome_aluno"):
        session['erro'] = 'Login falhou ou não foi possível extrair os dados. Verifique as suas credenciais.'
        session['nome_aluno'] = None
        session['nome_curso'] = None
        session['disciplinas'] = []
    else:
        # Armazena todos os dados do dicionário na sessão, para serem usados no HTML
        session['nome_aluno'] = dados_sigaa.get('nome_aluno', 'Aluno')
        session['nome_curso'] = dados_sigaa.get('nome_curso', 'Curso Desconhecido')
        session['disciplinas'] = dados_sigaa.get('disciplinas', [])
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Renderiza o 'dashboard.html' como a página de resultados
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)