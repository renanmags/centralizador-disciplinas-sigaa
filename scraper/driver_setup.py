# scraper/driver_setup.py

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

# REMOVEMOS TODAS AS IMPORTAÇÕES DO WEBDRIVER-MANAGER

def setup_driver(browser_name="auto"):
    """
    Configura o driver do Selenium. Se browser_name for 'auto', tenta detectar
    um navegador instalado. Usa o Selenium Manager embutido.
    """
    browser_name = browser_name.lower()
    detected_browser = None

    if browser_name == "auto":
        print("   -> Modo de detecção automática de navegador ativado.")
        preference_order = ["chrome", "brave", "firefox", "edge"]
        
        # O dicionário de caminhos agora é usado para DETECÇÃO e para o BINARY_LOCATION
        WINDOWS_BROWSER_PATHS = {
            "chrome": [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
            "brave": [r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"],
            "firefox": [r"C:\Program Files\Mozilla Firefox\firefox.exe", r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"],
            "edge": [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
        }
        
        for browser in preference_order:
            for path in WINDOWS_BROWSER_PATHS.get(browser, []):
                if os.path.exists(path):
                    print(f"   -> Navegador encontrado: {browser.capitalize()} em '{path}'")
                    detected_browser = browser
                    break
            if detected_browser:
                break
        
        if not detected_browser:
            raise Exception("Nenhum navegador suportado foi encontrado.")
        
        browser_name = detected_browser

    if browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        # Deixamos o Service vazio para o Selenium Manager agir
        driver = webdriver.Firefox(options=options)
    
    elif browser_name == "edge":
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        driver = webdriver.Edge(options=options)

    else: # Chrome ou Brave
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        # ... outras opções ...
        
        if browser_name == "brave":
            # Apontamos para o executável do Brave, o Selenium Manager vai achar o driver certo
            options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

        # A MÁGICA: Não passamos nenhum Service.
        # O Selenium Manager vai detectar a versão do browser (pelo binary_location se for Brave)
        # e baixar/usar o driver correto automaticamente.
        driver = webdriver.Chrome(options=options)

    print(f"   -> Usando o {browser_name.capitalize()} em modo headless via Selenium Manager.")
    return driver