# Imports para automação do navegador
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pathlib import Path
import os
import time

# Imports para extração de dados e salvamento
from bs4 import BeautifulSoup
import re
import json

def formatar_horario(horario_str):
    """
    Função auxiliar para agrupar e formatar os horários das disciplinas.
    """
    try:
        horario_limpo = horario_str.split('(')[0].replace('\n', '').replace('\r', '').strip()
        dias_semana = r'(SEG|TER|QUA|QUI|SEX|SAB)'
        partes = [p.strip() for p in re.split(dias_semana, horario_limpo) if p.strip()]
        horarios_agrupados = {}
        for i in range(0, len(partes), 2):
            dia, horario = partes[i], partes[i+1].replace('-', ' - ')
            if horario not in horarios_agrupados:
                horarios_agrupados[horario] = []
            horarios_agrupados[horario].append(dia)
        horarios_finais = []
        for horario, dias in horarios_agrupados.items():
            dias_formatados = " e ".join([d.title() for d in dias])
            horarios_finais.append(f"{dias_formatados} - {horario.replace('-', ' às ')}")
        return " / ".join(horarios_finais)
    except:
        return horario_str

def formatar_professores(professores_str):
    """
    Função auxiliar para separar múltiplos professores com ' / '.
    A lógica considera que o SIGAA pode usar ' e ' (minúsculo) como separador.
    """
    separador = " e "
    if separador in professores_str:
        professores_lista = professores_str.split(separador)
        nomes_formatados = [p.strip().title() for p in professores_lista]
        return " / ".join(nomes_formatados)
    else:
        return professores_str.strip().title()

def extrair_atividades(driver):
    """Extrai atividades pendentes do portal do discente com extração robusta."""
    try:
        print("   -> Procurando tabela de atividades...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tabela_soup = soup.select_one('#avaliacao-portal table')
        
        if not tabela_soup: 
            print("   -> Tabela de atividades não encontrada.")
            return []

        atividades = []
        linhas = tabela_soup.select('tbody tr')
        
        for linha in linhas:
            cols = linha.select("td")
            if len(cols) >= 3:
                data_texto = cols[1].text.strip()
                data_partes = data_texto.split('(')
                celula_descricao = cols[2]
                
                disciplina_nome_bruto = celula_descricao.small.contents[0]
                disciplina_nome = disciplina_nome_bruto.strip() if disciplina_nome_bruto else ""
                
                tarefa_tag = celula_descricao.find('a')
                tarefa_nome = tarefa_tag.text.strip() if tarefa_tag else ""
                
                tarefa_descricao = f"Tarefa: {tarefa_nome}" if tarefa_nome else ""

                atividades.append({
                    "data": data_partes[0].strip(),
                    "prazo_dias": data_partes[1].replace('dias)', '').strip() if len(data_partes) > 1 else None,
                    "disciplina_nome": disciplina_nome,
                    "tarefa_descricao": tarefa_descricao,
                    "concluida": 'check.png' in cols[0].decode_contents()
                })
        
        return atividades
    
    except Exception as e:
        print(f"   -> Nenhuma atividade encontrada ou erro ao extrair: {str(e)}")
        return []

def get_sigaa_disciplinas(username, password):
    """
    Função que usa Selenium para fazer login no SIGAA e extrair os dados
    detalhados das disciplinas e atividades.
    """
    # (NOVO) Marca o tempo de início da execução
    start_time = time.monotonic()
    
    print(f"--- Iniciando scraper para o usuário: {username} ---")
    
    options = Options()
    # Lembre-se de verificar se este caminho para o executável do seu navegador está correto.
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
        "nome_aluno": None, "nome_curso": None,
        "disciplinas": [], "atividades": []
    }

    debug_dir = "debug"
    os.makedirs(debug_dir, exist_ok=True)
    
    try:
        # --- ETAPA 1: LOGIN E NAVEGAÇÃO ATÉ O PORTAL ---
        print("   -> Acessando página de login...")
        driver.get('https://si3.ufc.br/sigaa/verTelaLogin.do')
        wait = WebDriverWait(driver, 8)
        
        campo_usuario = wait.until(EC.presence_of_element_located((By.NAME, "user.login")))
        campo_usuario.send_keys(username)
        campo_senha = driver.find_element(By.NAME, "user.senha")
        campo_senha.send_keys(password)
        campo_senha.submit()
        
        try:
            WebDriverWait(driver, 2).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Continuar >>']")),
                    EC.presence_of_element_located((By.LINK_TEXT, "Portal do Discente"))
                )
            )
        except:
            raise Exception("Página pós-login não reconhecida ou login inválido.")
        
        if "Avaliação Institucional" in driver.page_source:
            driver.find_element(By.CSS_SELECTOR, "input[value='Continuar >>']").click()
        
        link_portal_discente = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Portal do Discente")))
        link_portal_discente.click()
        
        wait.until(EC.title_contains("Portal do Discente"))
        print("   -> SUCESSO! Chegamos ao Portal do Discente.")

        # --- ETAPA 2: EXTRAIR ATIVIDADES PENDENTES ---
        print("   -> Extraindo atividades pendentes...")
        dados_retorno["atividades"] = extrair_atividades(driver)
        print(f"   -> Encontradas {len(dados_retorno['atividades'])} atividades")

        # --- ETAPA 3: NAVEGAR PELO MENU ATÉ O ATESTADO ---
        print("   -> Navegando para o Atestado de Matrícula...")
        menu_ensino = wait.until(EC.presence_of_element_located((By.XPATH, "//td[.//span[text()='Ensino']]")))
        actions = ActionChains(driver)
        actions.move_to_element(menu_ensino).perform()
        time.sleep(0.1)
        
        submenu_documentos = wait.until(EC.visibility_of_element_located((By.XPATH, "//td[text()='Documentos e Declarações']")))
        actions.move_to_element(submenu_documentos).perform()
        time.sleep(0.1)
        
        submenu_atestado = wait.until(EC.visibility_of_element_located((By.XPATH, "//td[text()='Atestado de Matrícula']")))
        submenu_atestado.click()
        
        # --- ETAPA 4: EXTRAÇÃO DOS DADOS DO ATESTADO ---
        print("   -> Extraindo dados do atestado...")
        wait.until(EC.presence_of_element_located((By.ID, 'identificacao')))
        
        html_atestado = driver.page_source
        soup = BeautifulSoup(html_atestado, 'html.parser')
        
        tabela_info_aluno = soup.find('table', id='identificacao')
        if tabela_info_aluno:
            for linha in tabela_info_aluno.find_all('tr'):
                celulas = linha.find_all('td')
                if len(celulas) >= 2:
                    label, valor = celulas[0].text.strip(), celulas[1].text.strip()
                    if "Nome:" in label:
                        dados_retorno["nome_aluno"] = " ".join(valor.title().split()[:2])
                    elif "Curso:" in label:
                        dados_retorno["nome_curso"] = valor.split(' - ')[0].strip().title()

        tabela_disciplinas = soup.find('table', id='matriculas')
        if tabela_disciplinas:
            for linha in tabela_disciplinas.find_all('tr')[1:]:
                colunas = linha.find_all('td')
                if len(colunas) >= 3:
                    componente_tag = colunas[0].find('span', class_='componente')
                    docente_tag = colunas[0].find('span', class_='docente')
                    horario_tag = colunas[2]
                    if componente_tag and docente_tag and horario_tag:
                        codigo_nome = componente_tag.text.strip().split(' - ')
                        disciplina_info = {
                            'codigo': codigo_nome[0].strip(),
                            'nome': codigo_nome[1].strip() if len(codigo_nome) > 1 else '',
                            'professor': formatar_professores(docente_tag.text),
                            'horario': formatar_horario(horario_tag.text.strip())
                        }
                        dados_retorno["disciplinas"].append(disciplina_info)
        
        return dados_retorno

    except Exception as e:
        print(f"   -> ERRO no scraper: {e}")
        screenshot_path = os.path.join(debug_dir, 'screenshot_erro.png')
        driver.save_screenshot(screenshot_path)
        print(f"   -> Screenshot do erro salvo em: {screenshot_path}")
        return dados_retorno
        
    finally:
        # --- ETAPA 5: SALVAR DADOS E FINALIZAR ---
        print("   -> Salvando dados capturados em arquivo JSON...")
        filepath = os.path.join(debug_dir, "dados_capturados.json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dados_retorno, f, ensure_ascii=False, indent=4)
            print(f"   -> SUCESSO! Dados salvos em: {filepath}")
        except Exception as e:
            print(f"   -> ERRO ao salvar o arquivo JSON: {e}")
        
        driver.quit()

        #Calcula e exibe o tempo total de execução
        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"\n--- Tempo de execução: {duration:.2f} segundos ---")


# --- Exemplo de como chamar a função ---
# if __name__ == '__main__':
#     # Substitua com seu usuário e senha
#     usuario_sigaa = "SEU_USUARIO_AQUI"
#     senha_sigaa = "SUA_SENHA_AQUI"
#     
#     dados_coletados = get_sigaa_disciplinas(usuario_sigaa, senha_sigaa)
#     
#     if dados_coletados.get("disciplinas"):
#         print("-> Dados das disciplinas coletadas com sucesso.")
#     else:
#         print("-> Não foi possível coletar os dados das disciplinas.")