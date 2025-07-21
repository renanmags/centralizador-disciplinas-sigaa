import re

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