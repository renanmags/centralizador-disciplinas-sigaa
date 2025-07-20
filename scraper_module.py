# Imports para automação do navegador
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

# Imports para extração de dados
from bs4 import BeautifulSoup
import re
import json

def formatar_horario(horario_str):
    """
    Função auxiliar para agrupar e formatar os horários das disciplinas.
    Exemplo de entrada: "TER 10:00-12:00QUI 10:00-12:00"
    Exemplo de saída: "Ter e Qui - 10:00 às 12:00"
    """
    try:
        # Limpa o texto, removendo quebras de linha e a data no final
        horario_limpo = horario_str.split('(')[0].replace('\n', '').replace('\r', '').strip()
        
        dias_semana = r'(SEG|TER|QUA|QUI|SEX|SAB)'
        partes = [p.strip() for p in re.split(dias_semana, horario_limpo) if p.strip()]
        
        horarios_agrupados = {}
        for i in range(0, len(partes), 2):
            dia = partes[i]
            # Mantém o horário original para agrupar corretamente
            horario = partes[i+1]
            
            if horario not in horarios_agrupados:
                horarios_agrupados[horario] = []
            horarios_agrupados[horario].append(dia)
            
        horarios_finais = []
        for horario, dias in horarios_agrupados.items():
            # Capitaliza a primeira letra de cada dia (ex: TER -> Ter)
            dias_capitalizados = [d.title() for d in dias]
            # Junta os dias com " e "
            dias_formatados = " e ".join(dias_capitalizados)
            # Formata a parte do horário, substituindo o hífen
            horario_formatado = horario.replace('-', ' às ')
            
            # Combina tudo no formato final desejado
            horarios_finais.append(f"{dias_formatados} - {horario_formatado}")
            
        return " / ".join(horarios_finais)
    except:
        # Se ocorrer um erro na formatação, retorna a string original
        return horario_str

def get_sigaa_disciplinas(username, password):
    """
    Função que usa Selenium para fazer login no SIGAA, navegar até o Atestado de Matrícula
    e extrair os dados detalhados das disciplinas.
    """
    print(f"--- Iniciando scraper para o usuário: {username} ---")
    
    options = Options()
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    
    # Para depurar, comente a linha abaixo. Para produção, descomente.
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
            WebDriverWait(driver, 5).until(
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

        # --- ETAPA 2: NAVEGAR PELO MENU ATÉ O ATESTADO ---
        print("   -> Navegando pelo menu para encontrar o Atestado...")
        
        menu_ensino = wait.until(EC.presence_of_element_located((By.XPATH, "//td[.//span[text()='Ensino']]")))
        actions = ActionChains(driver)
        actions.move_to_element(menu_ensino).perform()
        time.sleep(0.5) # Pausa para o submenu renderizar
        
        submenu_documentos = wait.until(EC.visibility_of_element_located((By.XPATH, "//td[text()='Documentos e Declarações']")))
        actions.move_to_element(submenu_documentos).perform()
        time.sleep(0.5) # Pausa para o submenu final renderizar
        
        submenu_atestado = wait.until(EC.visibility_of_element_located((By.XPATH, "//td[text()='Atestado de Matrícula']")))
        submenu_atestado.click()
        
        # --- ETAPA 3: EXTRAÇÃO DOS DADOS DO ATESTADO (LÓGICA CORRIGIDA) ---
        print("   -> Aguardando o carregamento dos dados do atestado...")
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Esperamos explicitamente que a tabela de identificação apareça na página
        # antes de tentarmos extrair o HTML.
        wait.until(EC.presence_of_element_located((By.ID, 'identificacao')))
        print("   -> Dados do atestado carregados. Extraindo...")
        
        html_atestado = driver.page_source
        soup = BeautifulSoup(html_atestado, 'html.parser')
        
        # Encontra a tabela de identificação pelo seu ID
        tabela_info_aluno = soup.find('table', id='identificacao')
        if tabela_info_aluno:
            for linha in tabela_info_aluno.find_all('tr'):
                celulas = linha.find_all('td')
                if len(celulas) >= 2:
                    label = celulas[0].text.strip()
                    valor = celulas[1].text.strip()
                    if "Nome:" in label:
                        nome_completo = valor.title()
                        dados_retorno["nome_aluno"] = " ".join(nome_completo.split()[:2])
                    elif "Curso:" in label:
                        curso_sem_sigla = valor.split(' - ')[0].strip()
                        dados_retorno["nome_curso"] = curso_sem_sigla.title()

        # Encontra a tabela de disciplinas pelo seu ID
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
                        codigo = codigo_nome[0].strip()
                        nome = codigo_nome[1].strip() if len(codigo_nome) > 1 else ''
                        
                        professor = docente_tag.text.strip().title()
                        horario = formatar_horario(horario_tag.text.strip())
                        
                        disciplina_info = {
                            'codigo': codigo, 'nome': nome,
                            'professor': professor, 'horario': horario
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
        # --- Funcionalidade de depuração ---
        print("   -> Salvando resultado em 'resultado_scraper.json' para depuração...")
        with open('resultado_scraper.json', 'w', encoding='utf-8') as f:
            json.dump(dados_retorno, f, indent=4, ensure_ascii=False)

        driver.quit()