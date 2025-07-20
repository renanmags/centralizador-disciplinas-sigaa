// Este código será executado assim que a estrutura da página estiver pronta
document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona o formulário de login
    const form = document.getElementById('loginForm');

    // Garante que o formulário existe na página antes de adicionar o "ouvinte"
    if (form) {
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('.submit-button');

            // Desativa o botão para impedir cliques múltiplos
            button.disabled = true;

            // Adiciona a classe 'loading' para que o CSS possa alterar a sua aparência
            button.classList.add('loading');
        });
    }
});