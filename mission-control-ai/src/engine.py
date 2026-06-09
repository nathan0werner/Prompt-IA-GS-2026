"""Motor de análise da Mission Control AI — Trilha 3 ConnectSat."""
import os
from ollama import Client
from dotenv import load_dotenv
from pathlib import Path

from src import telemetria
from src import alertas

load_dotenv()

# Identificação da trilha — ALTEREM conforme a escolha do grupo
TRILHA = "connectsat"  # "agrosat" | "envirosat" | "connectsat" | "mobilitysat"

API_KEY = os.environ.get("OLLAMA_API_KEY", "").strip()
# Placeholders comuns que indicam que a chave ainda não foi configurada
_PLACEHOLDERS = {"", "sua_chave_aqui_sem_aspas", "cole_sua_chave_real_aqui",
                 "sua_chave_aqui"}

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + API_KEY}
)


def llm(prompt, system=None, max_tokens=800, temperature=0.3):
    """Envia prompt ao gpt-oss:120b via Ollama Cloud."""
    # Pré-checagem: chave ausente ou ainda no valor de exemplo
    if API_KEY in _PLACEHOLDERS:
        return ("⚠ Chave da Ollama não configurada.\n"
                "Abra o arquivo .env na raiz e defina uma chave real:\n"
                "  OLLAMA_API_KEY=ok-...\n"
                "Pegue a chave em https://ollama.com → Settings → Keys.")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        return client.chat(
            model="gpt-oss:120b",
            messages=messages,
            options={"num_predict": max_tokens, "temperature": temperature},
            stream=False
        )['message']['content'].strip()
    except Exception as e:
        # Diagnóstico mais útil que a mensagem genérica
        detalhe = str(e)
        dica = ""
        low = detalhe.lower()
        if "401" in detalhe or "unauthorized" in low:
            dica = ("\n   → Chave inválida ou expirada. Confira o valor em .env "
                    "(sem aspas/espaços) e gere uma nova em ollama.com.")
        elif "403" in detalhe:
            dica = "\n   → Acesso negado. Verifique as permissões da sua chave."
        elif "404" in detalhe or "not found" in low:
            dica = ("\n   → Modelo não encontrado. Confirme o nome 'gpt-oss:120b' "
                    "no seu plano Ollama Cloud.")
        elif "429" in detalhe:
            dica = "\n   → Limite de uso atingido. Aguarde e tente novamente."
        elif any(k in low for k in ("timeout", "connection", "resolve",
                                    "network", "getaddrinfo", "ssl")):
            dica = ("\n   → Falha de rede/conexão. Verifique sua internet e se "
                    "https://ollama.com está acessível.")
        return f"⚠ Erro ao consultar IA: {detalhe}{dica}"


def load_system_prompt():
    """Lê o system prompt do arquivo prompts/system_prompt.md"""
    path = Path("prompts/system_prompt.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "Você é um assistente."  # fallback genérico


# Rótulos legíveis para cada parâmetro
ROTULOS = {
    "latencia_uplink_ms": "Latência uplink",
    "throughput_feixe_mbps": "Throughput do feixe",
    "saude_antena_pct": "Saúde antena phased-array",
    "beam_steering_erro_deg": "Erro de beam steering",
    "carga_termica_transponder_c": "Carga térmica transponder",
    "energia_bateria_pct": "Energia da bateria",
}
UNIDADES = {
    "latencia_uplink_ms": "ms",
    "throughput_feixe_mbps": "Mbps",
    "saude_antena_pct": "%",
    "beam_steering_erro_deg": "°",
    "carga_termica_transponder_c": "°C",
    "energia_bateria_pct": "%",
}

ICONE_NIVEL = {"OK": "🟢", "ATENCAO": "🟡", "CRITICO": "🔴"}


class MissionEngine:
    """Motor de análise — métodos implementados (foco do trabalho)."""

    def __init__(self, cenario=None):
        self.trilha = TRILHA
        self.system_prompt = load_system_prompt()
        # Se um cenário for passado, todas as leituras o usam (demonstração).
        self.cenario = cenario
        # True se a chave da Ollama parece configurada (não é placeholder).
        self.api_key_ok = API_KEY not in _PLACEHOLDERS

    def is_ready(self):
        # Pronto: analyze() está implementado.
        return True

    # ------------------------------------------------------------------ #
    # Helpers internos
    # ------------------------------------------------------------------ #
    def _coletar(self):
        return telemetria.coletar(cenario=self.cenario)

    def _formatar_telemetria(self, dados):
        linhas = []
        for param in ROTULOS:
            if param in dados:
                valor = dados[param]
                unid = UNIDADES.get(param, "")
                linhas.append(f"  • {ROTULOS[param]}: {valor} {unid}".rstrip())
        return "\n".join(linhas)

    def _formatar_alertas(self, lista):
        if not lista:
            return "  Nenhum alerta — todos os parâmetros nominais."
        linhas = []
        for a in lista:
            ico = ICONE_NIVEL.get(a["nivel"], "•")
            linhas.append(f"  {ico} [{a['nivel']}] {a['mensagem']}")
            linhas.append(f"      ↳ Impacto na Terra: {a['impacto_terra']}")
            if a["acao_auto"]:
                linhas.append(f"      ↳ {a['acao_auto']}")
        return "\n".join(linhas)

    # ------------------------------------------------------------------ #
    # Métodos usados pela UI
    # ------------------------------------------------------------------ #
    def status_snapshot(self):
        """Retorna texto resumindo o estado atual da telemetria."""
        dados = self._coletar()
        lista = alertas.avaliar(dados)
        estado = alertas.estado_geral(dados)
        ico = ICONE_NIVEL.get(estado, "•")

        bloco = []
        bloco.append(f"🛰 Satélite: {dados.get('satelite', 'ConnectSat-LEO-07')}")
        bloco.append(f"⏱ Timestamp: {dados.get('timestamp', '-')}")
        bloco.append(f"{ico} ESTADO GERAL: {estado}\n")
        bloco.append("📡 TELEMETRIA:")
        bloco.append(self._formatar_telemetria(dados))
        bloco.append("\n⚠ ALERTAS:")
        bloco.append(self._formatar_alertas(lista))
        return "\n".join(bloco)

    def impact_report(self):
        """Modo narrativa — dá palco para o impacto terrestre de cada alerta."""
        dados = self._coletar()
        lista = alertas.avaliar(dados)
        if not lista:
            return ("🌍 Nenhuma anomalia ativa. O ConnectSat está entregando "
                    "conectividade estável às comunidades rurais atendidas — "
                    "escolas, postos de telemedicina e pequenos negócios online.")
        linhas = ["🌍 TRADUÇÃO DO IMPACTO TERRESTRE\n"]
        for a in lista:
            ico = ICONE_NIVEL.get(a["nivel"], "•")
            linhas.append(f"{ico} {ROTULOS.get(a['parametro'], a['parametro'])} "
                          f"({a['nivel']})")
            linhas.append(f"   {a['impacto_terra']}")
            if a["acao_auto"]:
                linhas.append(f"   → {a['acao_auto']}")
            linhas.append("")
        return "\n".join(linhas).strip()

    def analyze(self, pergunta_usuario):
        """Analisa a pergunta com base na telemetria + alertas + IA."""
        # 1. Coletar dados
        dados = self._coletar()
        # 2. Avaliar alertas (lógica em código Python)
        lista = alertas.avaliar(dados)
        estado = alertas.estado_geral(dados)

        # 3. Montar prompt com dados REAIS + alertas + pergunta
        prompt = (
            f"### TELEMETRIA ATUAL ({dados.get('satelite')}) "
            f"— {dados.get('timestamp')}\n"
            f"{self._formatar_telemetria(dados)}\n\n"
            f"### ESTADO CLASSIFICADO PELA LÓGICA PYTHON: {estado}\n\n"
            f"### ALERTAS DETECTADOS (já classificados em código):\n"
            f"{self._formatar_alertas(lista)}\n\n"
            f"### PERGUNTA DO OPERADOR:\n{pergunta_usuario}\n\n"
            f"Analise com base nos dados acima. Para cada anomalia, amarre a "
            f"leitura técnica à consequência terrestre para as comunidades "
            f"rurais atendidas, seguindo o formato definido no system prompt."
        )

        # 4. Chamar a IA com o system prompt customizado
        resposta = llm(prompt, system=self.system_prompt)

        # 5. Retornar a resposta
        return resposta
