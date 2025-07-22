# Centralizador Acadêmico - SIGAA

## 📖 Sobre o Projeto

O Centralizador Acadêmico é uma aplicação web desenvolvida em Flask e Selenium que automatiza o acesso ao SIGAA (Sistema Integrado de Gestão de Atividades Acadêmicas) da UFC. A ferramenta faz o login em nome do usuário, extrai informações cruciais como disciplinas matriculadas e atividades pendentes, e as apresenta em um dashboard limpo e unificado.

Além dos dados extraídos automaticamente, a plataforma permite que o usuário adicione, gerencie e exclua seus próprios eventos (provas, trabalhos, lembretes), que ficam salvos localmente no navegador.

Este projeto foi criado para simplificar a vida acadêmica, centralizando informações importantes em um único lugar e oferecendo uma experiência de usuário mais moderna e agradável.

---

## ✨ Funcionalidades

* **Login Automatizado:** Acessa o SIGAA de forma segura para coletar os dados.
* **Dashboard Unificado:** Exibe disciplinas, professores, horários e atividades em um só lugar.
* **Eventos Personalizados:** Permite que o usuário crie, edite e exclua seus próprios eventos, que são salvos no navegador.
* **Diferenciação Visual:** Os eventos do SIGAA e os eventos criados pelo usuário são identificados por cores diferentes para fácil distinção.
* **Interface Responsiva:** Design limpo e funcional para uma melhor experiência.
* **Deploy na Nuvem:** Configurado para implantação em plataformas como a Render.

---

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído com as seguintes tecnologias:

* **Backend:**
    * ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
    * ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
    * ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
    * ![Beautiful Soup](https://img.shields.io/badge/Beautiful%20Soup-6c757d?style=for-the-badge&logo=python&logoColor=white)
    * ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=python&logoColor=white)
* **Frontend:**
    * ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
    * ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
    * ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
* **Deploy:**
    * ![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
    * ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
    * ![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

---

## 🚀 Como Rodar o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto no seu computador.

### Pré-requisitos

* [Python 3.8+](https://www.python.org/downloads/)
* Um navegador baseado em Chromium (Google Chrome, Brave, etc.) ou Firefox instalado.
* [Git](https://git-scm.com/downloads)

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
    cd NOME_DO_REPOSITORIO
    ```
    *Substitua `SEU_USUARIO` e `NOME_DO_REPOSITORIO` pelos seus dados.*

2.  **Crie e ative um ambiente virtual:**
    * No Windows:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    * No macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Execução

1.  **Inicie a aplicação Flask:**
    ```bash
    flask run
    ```

2.  **Acesse no navegador:**
    Abra seu navegador e vá para o endereço `http://127.0.0.1:5000`.

A página de login deverá aparecer, e você poderá usar suas credenciais do SIGAA para acessar o dashboard.

---

## 🏗️ Estrutura do Projeto