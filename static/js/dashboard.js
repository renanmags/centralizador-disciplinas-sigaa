document.addEventListener('DOMContentLoaded', function() {

    // --- PARTE 1: LÓGICA DO FORMULÁRIO ---
    const botaoMostrarForm = document.getElementById('btn-mostrar-form');
    const formContainer = document.getElementById('form-container');
    const formNovoEvento = document.getElementById('form-novo-evento'); // Definido aqui para ser usado por ambos os listeners
    
    if (botaoMostrarForm) {
        botaoMostrarForm.addEventListener('click', function() {
            formContainer.style.display = 'block';
            botaoMostrarForm.style.display = 'none';
        });
    }

    // (NOVO) Lógica para o botão de cancelar
    const botaoCancelar = document.getElementById('btn-cancelar');
    if (botaoCancelar) {
        botaoCancelar.addEventListener('click', function() {
            // 1. Esconde o formulário
            formContainer.style.display = 'none';
            // 2. Mostra o botão "+ Adicionar Evento" de volta
            botaoMostrarForm.style.display = 'block';
            // 3. Limpa qualquer campo que o usuário possa ter preenchido
            if(formNovoEvento) {
                formNovoEvento.reset();
            }
        });
    }


    // --- PARTE 2: ATIVAR O CALENDÁRIO INTELIGENTE (FLATPICKR) ---
    flatpickr("#evento-data", {
        dateFormat: "d/m/Y",
        allowInput: true,
        "locale": "pt"
    });

    // --- PARTE 3: LÓGICA DE GERENCIAMENTO DE EVENTOS ---
    const CHAVE_STORAGE = 'meusEventosManuais';

    function parseDataString(dataStr) {
        if (!dataStr || typeof dataStr !== 'string') return null;
        const parts = dataStr.split('/');
        if (parts.length !== 3) return null;
        const [dia, mes, ano] = parts;
        return new Date(ano, parseInt(mes, 10) - 1, dia);
    }

    function calcularDiasRestantes(dataDoEvento) {
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        const dataEventoObj = parseDataString(dataDoEvento);
        if (!dataEventoObj) return null;
        const diffTime = dataEventoObj.getTime() - hoje.getTime();
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    function carregarEventosManuais() {
        const eventosSalvos = localStorage.getItem(CHAVE_STORAGE);
        if (!eventosSalvos) return [];
        let todosEventosManuais = JSON.parse(eventosSalvos);
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        const eventosValidos = todosEventosManuais.filter(evento => {
            if (!evento.data) return false;
            const dataDoEvento = parseDataString(evento.data);
            return dataDoEvento && dataDoEvento >= hoje;
        });
        if (eventosValidos.length !== todosEventosManuais.length) {
            salvarEventosManuais(eventosValidos);
        }
        return eventosValidos;
    }

    function salvarEventosManuais(eventos) {
        localStorage.setItem(CHAVE_STORAGE, JSON.stringify(eventos));
    }

    // --- PARTE 4: LÓGICA DE RENDERIZAÇÃO ---
    const containerEventos = document.getElementById('lista-eventos-container');

    function renderizarTodosEventos() {
        const eventosManuais = carregarEventosManuais();
        
        const eventosSIGAANormalizados = atividadesSIGAA.map(ativ => ({
            id: ativ.disciplina_nome + ativ.data,
            titulo: `<strong>${ativ.disciplina_nome}</strong>`,
            descricao: `${ativ.tarefa_descricao}`,
            data: ativ.data,
            dias_restantes: ativ.prazo_dias,
            tipo: 'sigaa'
        }));

        let todosOsEventos = [...eventosSIGAANormalizados, ...eventosManuais];
        todosOsEventos.sort((a, b) => parseDataString(a.data) - parseDataString(b.data));

        containerEventos.innerHTML = '';

        if (todosOsEventos.length === 0) {
            containerEventos.innerHTML = '<p class="nenhuma-atividade">Nenhuma atividade/evento próximo encontrado.</p>';
            return;
        }

        const listaUl = document.createElement('ul');
        listaUl.className = 'event-list';

        todosOsEventos.forEach(evento => {
            const itemLi = document.createElement('li');
            
            if (evento.tipo === 'manual') {
                itemLi.classList.add('evento-manual');
            } else if (evento.tipo === 'sigaa') {
                itemLi.classList.add('evento-sigaa');
            }
            
            let diasRestantesTexto = '';
            let deleteButtonHTML = '';

            if (evento.tipo === 'manual') {
                deleteButtonHTML = `<span class="delete-btn" data-id="${evento.id}">&times;</span>`;
                const dias = calcularDiasRestantes(evento.data);
                if (dias >= 0) {
                    diasRestantesTexto = `(${dias} ${dias === 1 ? 'dia restante' : 'dias restantes'})`;
                }
            } else {
                const dias = evento.dias_restantes;
                diasRestantesTexto = `(${dias || '?'} ${dias === '1' ? 'dia restante' : 'dias restantes'})`;
            }

            const descricaoCompleta = `${evento.descricao || ''} ${diasRestantesTexto}`;

            itemLi.innerHTML = `
                ${deleteButtonHTML}
                ${evento.titulo}
                <br>
                ${descricaoCompleta} – <strong>${evento.data}</strong>
            `;
            listaUl.appendChild(itemLi);
        });

        containerEventos.appendChild(listaUl);
    }

    // --- PARTE 5: LÓGICA DO FORMULÁRIO DE SALVAR ---
    if (formNovoEvento) {
        formNovoEvento.addEventListener('submit', function(e) {
            e.preventDefault();
            const nomeAtividade = document.getElementById('evento-titulo').value;
            const disciplinaSelecionada = document.getElementById('evento-disciplina').value;
            const dataFormatada = document.getElementById('evento-data').value;
            const descricaoAdicional = document.getElementById('evento-descricao').value;
            
            if (!disciplinaSelecionada) { return alert('Por favor, selecione uma disciplina.'); }
            if (!dataFormatada || dataFormatada.length < 10) { return alert('Por favor, insira uma data válida no formato dd/mm/aaaa.'); }

            let descricaoFinal = `Tarefa: ${nomeAtividade}`;
            if (descricaoAdicional) { descricaoFinal += ` - ${descricaoAdicional}`; }

            const novoEvento = {
                id: Date.now(),
                titulo: `<strong>${disciplinaSelecionada}</strong>`,
                data: dataFormatada,
                descricao: descricaoFinal,
                tipo: 'manual'
            };

            const eventosAtuais = carregarEventosManuais();
            eventosAtuais.push(novoEvento);
            salvarEventosManuais(eventosAtuais);

            alert('Evento adicionado com sucesso!');
            formNovoEvento.reset();
            formContainer.style.display = 'none';
            botaoMostrarForm.style.display = 'block';
            renderizarTodosEventos();
        });
    }

    // --- PARTE 6: LÓGICA PARA EXCLUIR EVENTOS ---
    containerEventos.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Tem certeza que deseja excluir este evento?')) {
                const eventId = Number(e.target.dataset.id);
                let eventosAtuais = carregarEventosManuais();
                let eventosAtualizados = eventosAtuais.filter(evento => evento.id !== eventId);
                salvarEventosManuais(eventosAtualizados);
                renderizarTodosEventos();
            }
        }
    });

    // --- INICIALIZAÇÃO ---
    renderizarTodosEventos();
});