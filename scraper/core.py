# scraper/core.py

# Imports de bibliotecas externas
import os
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Importa a função do novo arquivo de setup
from .driver_setup import setup_driver
# Importa as funções auxiliares do nosso próprio pacote
from .utils import formatar_horario, formatar_professores


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


def get_sigaa_disciplinas(username, password, browser="auto"):
    """
    Função que usa Selenium para fazer login no SIGAA e extrair dados.
    Aceita um argumento 'browser' para escolher entre 'chrome', 'firefox', 'edge', 'brave'.
    """
    start_time = time.monotonic()
    
    print(f"--- Iniciando scraper para o usuário: {username} ---")
    
    driver = setup_driver(browser)
    
    dados_retorno = {
        "nome_aluno": None, "nome_curso": None,
        "disciplinas": [], "atividades": []
    }
    debug_dir = "debug"
    os.makedirs(debug_dir, exist_ok=True)
    
    try:
        print("   -> Acessando página de login...")
        driver.get('https://si3.ufc.br/sigaa/verTelaLogin.do')
        # (ALTERADO) Aumentado o wait principal para 25 segundos
        wait = WebDriverWait(driver, 25)
        
        campo_usuario = wait.until(EC.presence_of_element_located((By.NAME, "user.login")))
        campo_usuario.send_keys(username)
        campo_senha = driver.find_element(By.NAME, "user.senha")
        campo_senha.send_keys(password)
        campo_senha.submit()
        
        try:
            # (ALTERADO) Aumentado o wait pós-login para 25 segundos
            WebDriverWait(driver, 25).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Continuar >>']")),
                    EC.presence_of_element_located((By.LINK_TEXT, "Portal do Discente"))
                )
            )
        except Exception as e:
            raise Exception(f"Página pós-login não reconhecida ou login inválido (timeout de 25s). Erro: {e}")
        
        if "Avaliação Institucional" in driver.page_source:
            driver.find_element(By.CSS_SELECTOR, "input[value='Continuar >>']").click()
        
        link_portal_discente = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Portal do Discente")))
        link_portal_discente.click()
        
        wait.until(EC.title_contains("Portal do Discente"))
        print("   -> SUCESSO! Chegamos ao Portal do Discente.")

        print("   -> Extraindo atividades pendentes...")
        dados_retorno["atividades"] = extrair_atividades(driver)
        print(f"   -> Encontradas {len(dados_retorno['atividades'])} atividades")

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
        try:
            html_do_erro = driver.page_source
            caminho_erro_html = os.path.join(debug_dir, "pagina_de_erro.html")
            with open(caminho_erro_html, "w", encoding="utf-8") as f:
                f.write(html_do_erro)
            print(f"   -> HTML da página de erro salvo em: {caminho_erro_html}")
        except Exception as save_e:
            print(f"   -> Falha ao salvar o HTML da página de erro: {save_e}")
            
        screenshot_path = os.path.join(debug_dir, 'screenshot_erro.png')
        driver.save_screenshot(screenshot_path)
        print(f"   -> Screenshot do erro salvo em: {screenshot_path}")
        return dados_retorno
        
    finally:
        print("   -> Salvando dados capturados em arquivo JSON...")
        filepath = os.path.join(debug_dir, "dados_capturados.json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dados_retorno, f, ensure_ascii=False, indent=4)
            print(f"   -> SUCESSO! Dados salvos em: {filepath}")
        except Exception as e:
            print(f"   -> ERRO ao salvar o arquivo JSON: {e}")
        
        if 'driver' in locals() and driver:
            driver.quit()

        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"\n--- Tempo de execução: {duration:.2f} segundos ---")