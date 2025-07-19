document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona o formulário de login
    const form = document.getElementById('loginForm');

    // Garante que o formulário existe na página antes de adicionar o "ouvinte"
    if (form) {
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('.submit-button');
            
            // Esconde o texto e mostra o loader
            button.querySelector('.button-text').style.display = 'none';
            
            const loader = button.querySelector('.loader');
            if(loader) {
                loader.style.display = 'block';
            }

            // Desativa o botão
            button.disabled = true;
            button.style.cursor = 'not-allowed';
        });
    }
});