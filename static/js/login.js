document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        const submitButton = loginForm.querySelector('.submit-button');
        const buttonText = submitButton.querySelector('.button-text');
        const originalButtonText = buttonText.textContent; // Salva o texto original "Acessar"

        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // --- Ativar estado de carregamento ---
            submitButton.disabled = true; // Desativa o botão
            submitButton.classList.add('loading'); // Adiciona a classe para mudar a cor/cursor
            // Muda o texto e adiciona os spans para a animação
            buttonText.innerHTML = `Acessando<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>`;

            fetch('/login', {
                method: 'POST',
                body: new FormData(loginForm)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = data.redirect_url;
                } else {
                    window.location.reload(); // Recarrega para mostrar a msg de erro do Flask
                }
            })
            .catch(error => {
                console.error('Erro na requisição de login:', error);
                alert('Ocorreu um erro de comunicação. Tente novamente.');
                // Em caso de erro, reverte o botão ao estado original
                revertButton();
            });
        });

        // Função para reverter o botão ao estado normal
        function revertButton() {
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
            buttonText.textContent = originalButtonText;
        }
    }
});