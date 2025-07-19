# Imports para automação do navegador
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Imports para extração de dados
from bs4 import BeautifulSoup
import re

def formatar_horario(horario_str):
    """
    Função auxiliar para agrupar dias da semana com horários idênticos.
    Exemplo de entrada: "TER 10:00-12:00QUI 10:00-12:00"
    Exemplo de saída: "TER e QUI 10:00 - 12:00"
    """
    try:
        dias_semana = r'(SEG|TER|QUA|QUI|SEX|SAB)'
        partes = [p.strip() for p in re.split(dias_semana, horario_str) if p.strip()]
        
        horarios_agrupados = {}
        for i in range(0, len(partes), 2):
            dia = partes[i]
            horario = partes[i+1].replace('-', ' - ')
            
            if horario not in horarios_agrupados:
                horarios_agrupados[horario] = []
            horarios_agrupados[horario].append(dia)
            
        horarios_finais = []
        for horario, dias in horarios_agrupados.items():
            dias_formatados = " e ".join(dias)
            horarios_finais.append(f"{dias_formatados} {horario}")
            
        return " / ".join(horarios_finais)
    except:
        return horario_str

def get_sigaa_disciplinas(username, password):
    """
    Função que usa Selenium para fazer login no SIGAA e extrair os dados do aluno.
    Recebe: usuário e senha.
    Retorna: um dicionário contendo o nome do aluno, o curso e uma lista de disciplinas.
    """
    print(f"--- Iniciando scraper para o usuário: {username} ---")
    
    options = Options()
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    options.add_argument("--headless")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    
    dados_retorno = {
        "nome_aluno": None,
        "nome_curso": None,
        "disciplinas": []
    }
    
    try:
        # --- ETAPA 1: LOGIN E NAVEGAÇÃO ---
        print("   -> Acessando página de login...")
        driver.get('https://si3.ufc.br/sigaa/verTelaLogin.do')
        wait = WebDriverWait(driver, 15)
        
        campo_usuario = wait.until(EC.presence_of_element_located((By.NAME, "user.login")))
        campo_usuario.send_keys(username)
        campo_senha = driver.find_element(By.NAME, "user.senha")
        campo_senha.send_keys(password)
        campo_senha.submit()
        
        print("   -> Login submetido. Verificando páginas intermediárias...")
        try:
            WebDriverWait(driver, 5).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Continuar >>']")),
                    EC.presence_of_element_located((By.LINK_TEXT, "Portal do Discente"))
                )
            )
        except:
            raise Exception("Página pós-login não reconhecida ou login inválido.")
        
        if "Avaliação Institucional" in driver.page_source:
            print("   -> Página de avaliação encontrada. Clicando em 'Continuar'...")
            driver.find_element(By.CSS_SELECTOR, "input[value='Continuar >>']").click()
        
        print("   -> Acessando o Portal do Discente...")
        link_portal_discente = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Portal do Discente")))
        link_portal_discente.click()
        
        wait.until(EC.title_contains("Portal do Discente"))
        print("   -> SUCESSO! Chegamos ao Portal do Discente.")
        
        # --- ETAPA 2: EXTRAÇÃO DOS DADOS ---
        print("   -> Extraindo dados...")
        time.sleep(1)
        html_da_pagina_logada = driver.page_source
        soup = BeautifulSoup(html_da_pagina_logada, 'html.parser')
        
        cabecalho_dados = soup.find('h4', string='Dados Institucionais')
        if cabecalho_dados:
            print("   -> Bloco 'Dados Institucionais' encontrado.")
            tabela_dados = cabecalho_dados.find_next_sibling('table')
            if tabela_dados:
                for linha in tabela_dados.find_all('tr'):
                    celulas = linha.find_all('td')
                    if len(celulas) == 2:
                        label = celulas[0].text.strip()
                        valor = celulas[1].text.strip()
                        if "Curso:" in label:
                            # --- CORREÇÃO APLICADA AQUI ---
                            # Dividimos a string no primeiro hífen e pegamos a primeira parte.
                            # O .strip() final remove todos os espaços em branco à volta.
                            if "-" in valor:
                                curso_sem_sigla = valor.split('-')[0].strip()
                            else:
                                curso_sem_sigla = valor
                            
                            dados_retorno["nome_curso"] = curso_sem_sigla.title()
                            print(f"   -> Nome do curso encontrado e formatado: {dados_retorno['nome_curso']}")
        else:
            print("   -> AVISO: Bloco 'Dados Institucionais' não encontrado.")

        nome_aluno_tag = soup.select_one("div.nome_usuario p")
        if nome_aluno_tag:
            nome_completo = nome_aluno_tag.text.strip().title()
            partes_nome = nome_completo.split()
            primeiros_dois_nomes = " ".join(partes_nome[:2])
            dados_retorno["nome_aluno"] = primeiros_dois_nomes

        cabecalho_turmas = soup.find('h4', string=re.compile(r'Turmas do Semestre'))
        if cabecalho_turmas:
            tabela_disciplinas = cabecalho_turmas.find_next_sibling('table')
            if tabela_disciplinas:
                for linha in tabela_disciplinas.find_all('tr')[1:]:
                    colunas = linha.find_all('td')
                    if len(colunas) >= 4:
                        nome_completo = colunas[0].text.strip()
                        partes = nome_completo.split(' - ', 1)
                        codigo = partes[0]
                        nome = partes[1] if len(partes) > 1 else ''
                        
                        local_horario_completo = colunas[3].text.strip()
                        horario_apenas = local_horario_completo.split('(')[0].strip()
                        
                        horario_formatado = formatar_horario(horario_apenas)
                        
                        disciplina_info = {
                            'codigo': codigo, 'nome': nome,
                            'turma': colunas[1].text.strip(),
                            'carga_horaria': colunas[2].text.strip(),
                            'local_horario': horario_formatado
                        }
                        dados_retorno["disciplinas"].append(disciplina_info)
        
        return dados_retorno

    except Exception as e:
        print(f"   -> ERRO no scraper: {e}")
        driver.save_screenshot('screenshot_erro.png')
        print("   -> Captura de ecrã do erro salva em 'screenshot_erro.png'")
        return dados_retorno
        
    finally:
        print("--- Finalizando scraper ---")
        driver.quit()
