# scraper/driver_setup.py

import os
import platform  # Importa a biblioteca para detectar o sistema operacional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

def setup_driver(browser_name="auto"):
    """
    Configura o driver do Selenium de forma inteligente.
    - Em modo 'auto', detecta o navegador instalado no Windows.
    - Em ambiente Linux (produção), assume que o Chrome está instalado.
    - Usa o Selenium Manager embutido.
    """
    browser_name = browser_name.lower()
    system = platform.system()

    if browser_name == "auto":
        print("   -> Modo de detecção automática de navegador ativado.")
        
        if system == "Windows":
            # Lógica de detecção para o ambiente local (Windows)
            preference_order = ["chrome", "brave", "firefox", "edge"]
            WINDOWS_BROWSER_PATHS = {
                "chrome": [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
                "brave": [r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"],
                "firefox": [r"C:\Program Files\Mozilla Firefox\firefox.exe", r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"],
                "edge": [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
            }
            
            detected_browser = None
            for browser in preference_order:
                for path in WINDOWS_BROWSER_PATHS.get(browser, []):
                    if os.path.exists(path):
                        print(f"   -> Navegador encontrado: {browser.capitalize()} em '{path}'")
                        detected_browser = browser
                        break
                if detected_browser:
                    break
            
            if not detected_browser:
                raise Exception("Nenhum navegador suportado foi encontrado no Windows.")
            
            browser_name = detected_browser

        elif system == "Linux":
            # Em produção (Render/Linux), nosso script build.sh instala o Chrome.
            # Podemos assumir que ele existe.
            print("   -> Ambiente Linux (produção) detectado. Usando Chrome.")
            browser_name = "chrome"
        
        else:
            # Para outros sistemas como macOS, podemos adicionar a lógica depois. Por enquanto, usa Chrome.
            print(f"   -> Sistema operacional '{system}' não configurado para detecção. Usando Chrome por padrão.")
            browser_name = "chrome"

    # --- Configuração das Opções e Inicialização do Driver ---
    
    if browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    
    elif browser_name == "edge":
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        driver = webdriver.Edge(options=options)

    else: # Chrome ou Brave
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--window-size=1920,1080")
        
        # Opções cruciais para rodar em servidores Linux (e não fazem mal no Windows)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if system == "Windows" and browser_name == "brave":
            # Aponta para o executável do Brave apenas se estiver no Windows
            options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

        driver = webdriver.Chrome(options=options)

    print(f"   -> Usando o {browser_name.capitalize()} em modo headless via Selenium Manager.")
    return driver