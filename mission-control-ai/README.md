# 🚀 Mission Control AI — ConnectSat (Conectividade Rural)

## Integrantes
- Nome Completo — RM: XXXXXX — Turma: XCCXX
- Nome Completo — RM: XXXXXX — Turma: XCCXX
- Nome Completo — RM: XXXXXX — Turma: XCCXX

## O que o projeto faz
Mission Control AI é um sistema de monitoramento operacional de um **satélite de
telecomunicações em LEO** (estilo Starlink/OneWeb) dedicado à conectividade rural.
Ele gera telemetria simulada (latência de uplink, throughput do feixe, saúde da
antena phased-array, beam steering, carga térmica do transponder e energia),
detecta anomalias por **lógica de thresholds em Python** e dispara respostas
automatizadas. A **IA generativa (gpt-oss:120b via Ollama Cloud)** interpreta o
estado da missão em linguagem natural, sempre **traduzindo cada anomalia técnica
no impacto real para as comunidades atendidas** — escolas rurais, telemedicina e
pequenos negócios sem fibra.

## Persona atendida
**NOC engineer da operadora** (engenheiro de plantão no Network Operations Center),
com apoio ao **coordenador de programa de inclusão digital**. Justificativa: é quem
recebe os alertas em tempo real e precisa entender, em segundos, tanto a falha
técnica quanto a consequência para o cliente final na comunidade rural.

## Tecnologias utilizadas
- Python 3.10+
- Ollama Cloud API (modelo `gpt-oss:120b`)
- Bibliotecas: `ollama`, `python-dotenv`, `rich`, `prompt-toolkit`, `pyfiglet`

## Como executar
1. Clone o repositório
2. Crie ambiente virtual: `python -m venv .venv && source .venv/bin/activate`
3. Instale dependências: `pip install -r requirements.txt`
4. Crie arquivo `.env` na raiz com: `OLLAMA_API_KEY=sua_chave_aqui`
5. Execute: `python main.py`

Comandos da CLI: `/help` `/status` `/impact` `/about` `/clear` `/exit`.
Qualquer outra entrada é enviada ao motor de análise por IA.

## Demonstração
![Banner inicial do sistema](assets/screenshot_banner.png)
![Alerta crítico com análise da IA](assets/screenshot_analise.png)

## System Prompt
O system prompt completo está em [`prompts/system_prompt.md`](prompts/system_prompt.md).
Ele define **papel** (analista de NOC do ConnectSat), **escopo** (6 parâmetros da
missão), **restrições** (só usa dados recebidos, não decide criticidade),
**tom** (operador experiente, calmo) e **formato de saída** estruturado. A regra de
ouro obriga o modelo a amarrar, em toda anomalia, a leitura técnica à consequência
terrestre.

## Cenários de teste demonstrados
Disponíveis em `data/cenarios.json`:
1. **normal** — todos os parâmetros dentro do range
2. **termica_critica** — carga térmica do transponder crítica + ação automática (modo economia térmica)
3. **perda_comunicacao** — latência altíssima e throughput colapsado
4. **energia_baixa** — bateria crítica em eclipse + modo economia de energia
5. **extremo_impossivel** — valores de borda (teste de robustez)

## Limitações conhecidas
- Os dados de telemetria são **simulados** e plausíveis, não fisicamente precisos.
- O sistema **não** rastreia órbita real nem efemérides; não há ingestão de dados ao vivo.
- A IA é **não-determinística**: a mesma entrada pode gerar respostas com pequenas
  variações de redação (mitigado com `temperature=0.3` e formato fixo no prompt).
- A decisão de criticidade é 100% Python; a IA apenas explica — ela não cria alertas.
- Requer conexão com a internet e chave válida da Ollama Cloud.

## Vídeo de demonstração
🎥 [Assistir no YouTube](https://www.youtube.com/watch?v=)
