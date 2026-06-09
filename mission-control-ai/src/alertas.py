"""Thresholds e regras de decisão — Trilha 3 ConnectSat.

Toda a lógica de "é crítico ou não?" vive aqui, em código Python.
A IA serve para EXPLICAR e CONTEXTUALIZAR — não para decidir.

Cada alerta carrega:
    - nivel        : "OK" | "ATENCAO" | "CRITICO"
    - parametro    : nome do parâmetro avaliado
    - valor        : valor lido
    - mensagem     : descrição técnica
    - impacto_terra: tradução do que isso significa para o cliente terrestre
    - acao_auto    : resposta automatizada acionada pelo sistema (ou None)
"""

# Thresholds: (limite_atencao, limite_critico, direcao)
# direcao "acima"  -> valores ALTOS são ruins
# direcao "abaixo" -> valores BAIXOS são ruins
THRESHOLDS = {
    "latencia_uplink_ms":          (80, 120, "acima"),
    "throughput_feixe_mbps":       (100, 60, "abaixo"),
    "saude_antena_pct":            (85, 70, "abaixo"),
    "beam_steering_erro_deg":      (1.0, 2.0, "acima"),
    "carga_termica_transponder_c": (75, 85, "acima"),
    "energia_bateria_pct":         (40, 20, "abaixo"),
}

# Tradução de cada parâmetro para o impacto terrestre (diferencial da trilha)
IMPACTO_TERRA = {
    "latencia_uplink_ms":
        "Aulas online em escolas rurais travam; teleconsultas de telemedicina "
        "ficam com áudio/vídeo defasados, comprometendo o diagnóstico remoto.",
    "throughput_feixe_mbps":
        "A banda do feixe cai: famílias e pequenos negócios da comunidade "
        "perdem velocidade — downloads de material escolar e PIX/maquininhas "
        "ficam lentos ou indisponíveis.",
    "saude_antena_pct":
        "A antena phased-array degradada reduz a cobertura efetiva sobre a "
        "região rural atendida, podendo deixar setores inteiros sem sinal.",
    "beam_steering_erro_deg":
        "O feixe deixa de apontar com precisão para a célula rural-alvo: o sinal "
        "se espalha para áreas erradas e a comunidade contratada fica descoberta.",
    "carga_termica_transponder_c":
        "Superaquecimento do transponder ameaça desligamentos de proteção que "
        "derrubam o serviço de toda a região durante a passagem do satélite.",
    "energia_bateria_pct":
        "Bateria baixa (período de eclipse) força corte de feixes para poupar "
        "energia — comunidades de menor prioridade ficam temporariamente offline.",
}

# Respostas automatizadas para situações críticas (decisão em código)
ACOES_CRITICAS = {
    "latencia_uplink_ms":
        "AÇÃO AUTO: rotear tráfego prioritário (telemedicina/escolas) por "
        "satélite vizinho na constelação e reduzir QoS de tráfego não essencial.",
    "throughput_feixe_mbps":
        "AÇÃO AUTO: ativar realocação dinâmica de banda, concentrando o feixe "
        "remanescente nas células de maior prioridade social.",
    "saude_antena_pct":
        "AÇÃO AUTO: acionar elementos redundantes da phased-array e abrir ticket "
        "de manutenção no NOC.",
    "beam_steering_erro_deg":
        "AÇÃO AUTO: executar recalibração de apontamento (beam steering) e travar "
        "o feixe na última posição válida até estabilizar.",
    "carga_termica_transponder_c":
        "AÇÃO AUTO: entrar em MODO ECONOMIA TÉRMICA — reduzir potência do "
        "transponder e reorientar painéis para dissipar calor.",
    "energia_bateria_pct":
        "AÇÃO AUTO: entrar em MODO ECONOMIA DE ENERGIA — desligar feixes "
        "secundários e preservar carga para os serviços essenciais.",
}


def _classificar(param, valor):
    """Retorna o nível do parâmetro segundo os thresholds em código."""
    if param not in THRESHOLDS:
        return "OK"
    atencao, critico, direcao = THRESHOLDS[param]
    if direcao == "acima":
        if valor >= critico:
            return "CRITICO"
        if valor >= atencao:
            return "ATENCAO"
        return "OK"
    else:  # abaixo
        if valor <= critico:
            return "CRITICO"
        if valor <= atencao:
            return "ATENCAO"
        return "OK"


def avaliar(dados):
    """Avalia a telemetria e retorna a lista de alertas.

    Esta é a lógica de decisão central, toda em Python.
    """
    alertas = []
    for param, valor in dados.items():
        if param not in THRESHOLDS:
            continue
        nivel = _classificar(param, valor)
        if nivel == "OK":
            continue
        atencao, critico, direcao = THRESHOLDS[param]
        limite = critico if nivel == "CRITICO" else atencao
        comparador = "≥" if direcao == "acima" else "≤"
        alerta = {
            "nivel": nivel,
            "parametro": param,
            "valor": valor,
            "mensagem": (f"{param} = {valor} (limiar {nivel.lower()} "
                         f"{comparador} {limite})"),
            "impacto_terra": IMPACTO_TERRA.get(param, "Impacto não mapeado."),
            "acao_auto": ACOES_CRITICAS.get(param) if nivel == "CRITICO" else None,
        }
        alertas.append(alerta)
    return alertas


def alerta_critico(dados):
    """Retorna True se houver pelo menos um parâmetro em nível CRÍTICO."""
    return any(a["nivel"] == "CRITICO" for a in avaliar(dados))


def estado_geral(dados):
    """Resume o estado geral da missão: OK / ATENCAO / CRITICO."""
    alertas = avaliar(dados)
    if any(a["nivel"] == "CRITICO" for a in alertas):
        return "CRITICO"
    if any(a["nivel"] == "ATENCAO" for a in alertas):
        return "ATENCAO"
    return "OK"
