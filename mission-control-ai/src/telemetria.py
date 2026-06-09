"""Geração dos dados simulados de telemetria — Trilha 3 ConnectSat.

Satélite de telecomunicações em LEO (estilo Starlink/OneWeb).
Parâmetros monitorados:
    - latencia_uplink_ms      : latência do uplink em milissegundos
    - throughput_feixe_mbps   : vazão do feixe (beam) em Mbps
    - saude_antena_pct        : saúde da antena phased-array (0-100%)
    - beam_steering_erro_deg  : erro de apontamento do feixe em graus
    - carga_termica_transponder_c : carga térmica do transponder em °C
    - energia_bateria_pct     : carga da bateria (modo eclipse) em %

Os dados podem ser gerados aleatoriamente ou lidos de cenários
pré-definidos em data/cenarios.json para demonstração reproduzível.
"""
import json
import random
from pathlib import Path
from datetime import datetime, timezone

# Faixas nominais (operação normal) de cada parâmetro
FAIXA_NOMINAL = {
    "latencia_uplink_ms": (20, 45),
    "throughput_feixe_mbps": (150, 280),
    "saude_antena_pct": (88, 100),
    "beam_steering_erro_deg": (0.0, 0.5),
    "carga_termica_transponder_c": (30, 65),
    "energia_bateria_pct": (55, 100),
}

CENARIOS_PATH = Path("data/cenarios.json")


def _gerar_aleatorio():
    """Gera uma leitura plausível. Há chance de injetar uma anomalia
    para que a demonstração mostre alertas sem depender de sorte pura."""
    dados = {}
    for param, (lo, hi) in FAIXA_NOMINAL.items():
        if isinstance(lo, float) or isinstance(hi, float):
            dados[param] = round(random.uniform(lo, hi), 2)
        else:
            dados[param] = round(random.uniform(lo, hi), 1)

    # ~35% das leituras introduzem uma anomalia em um parâmetro sorteado
    if random.random() < 0.35:
        anomalia = random.choice(list(FAIXA_NOMINAL.keys()))
        if anomalia == "latencia_uplink_ms":
            dados[anomalia] = round(random.uniform(120, 400), 1)
        elif anomalia == "throughput_feixe_mbps":
            dados[anomalia] = round(random.uniform(0, 60), 1)
        elif anomalia == "saude_antena_pct":
            dados[anomalia] = round(random.uniform(20, 70), 1)
        elif anomalia == "beam_steering_erro_deg":
            dados[anomalia] = round(random.uniform(2.0, 8.0), 2)
        elif anomalia == "carga_termica_transponder_c":
            dados[anomalia] = round(random.uniform(85, 130), 1)
        elif anomalia == "energia_bateria_pct":
            dados[anomalia] = round(random.uniform(5, 30), 1)

    dados["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dados["satelite"] = "ConnectSat-LEO-07"
    return dados


def _carregar_cenario(nome):
    """Carrega um cenário nomeado de data/cenarios.json, se existir."""
    if not CENARIOS_PATH.exists():
        return None
    try:
        cenarios = json.loads(CENARIOS_PATH.read_text(encoding="utf-8"))
        for c in cenarios.get("cenarios", []):
            if c.get("nome") == nome:
                dados = dict(c["dados"])
                dados.setdefault(
                    "timestamp",
                    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
                dados.setdefault("satelite", "ConnectSat-LEO-07")
                return dados
    except (json.JSONDecodeError, KeyError):
        return None
    return None


def coletar(cenario=None):
    """Retorna um dicionário com a leitura atual da telemetria.

    Se `cenario` for informado e existir em data/cenarios.json, usa-o
    (útil para demonstração reproduzível). Caso contrário, gera dados
    aleatórios plausíveis.
    """
    if cenario:
        dados = _carregar_cenario(cenario)
        if dados is not None:
            return dados
    return _gerar_aleatorio()


def listar_cenarios():
    """Lista os nomes dos cenários disponíveis no JSON."""
    if not CENARIOS_PATH.exists():
        return []
    try:
        cenarios = json.loads(CENARIOS_PATH.read_text(encoding="utf-8"))
        return [c.get("nome") for c in cenarios.get("cenarios", [])]
    except (json.JSONDecodeError, KeyError):
        return []
