"""Interface CLI estilo Claude Code — usa Rich + prompt-toolkit."""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
import pyfiglet
from datetime import datetime

console = Console()
session = PromptSession(style=Style.from_dict({"prompt": "#06B6D4 bold"}))


def show_banner():
    """Exibe banner ASCII colorido no início."""
    banner = pyfiglet.figlet_format("Mission Control", font="ansi_shadow")
    console.print(Text(banner, style="bold #06B6D4"))
    console.print(Panel.fit(
        "Bem-vindo à interface da Mission Control AI.\n"
        "Sistema de monitoramento e análise por IA generativa.\n"
        "Trilha 3 — ConnectSat · Conectividade Rural (LEO)\n"
        "Use /help para ver os comandos · /exit para sair.\n"
        "Modelo: gpt-oss:120b via Ollama Cloud",
        title=" ◆ MISSION CONTROL", border_style="#06B6D4",
        subtitle="connected"
    ))


def show_response(text):
    """Renderiza resposta da IA em painel com timestamp."""
    now = datetime.now().strftime("%H:%M")
    console.print(Panel(text, title=" ◆ Mission Control",
                  subtitle=now, border_style="#06B6D4"))


def show_help():
    """Tabela de comandos disponíveis."""
    table = Table(title=" ◆ Comandos disponíveis", border_style="#06B6D4",
                  title_style="bold #06B6D4")
    table.add_column("Comando", style="bold #A855F7")
    table.add_column("Descrição", style="white")
    table.add_row("/help", "Mostra esta tabela de comandos")
    table.add_row("/status", "Snapshot atual da telemetria do satélite")
    table.add_row("/impact", "Modo narrativa — traduz alertas em impacto terrestre")
    table.add_row("/about", "Sobre o projeto e a trilha")
    table.add_row("/clear", "Limpa a tela e reexibe o banner")
    table.add_row("/exit", "Encerra a sessão")
    table.add_row("<pergunta>", "Envia a pergunta ao motor de análise por IA")
    console.print(table)


def show_about():
    console.print(Panel(
        "[bold #06B6D4]ConnectSat — Mission Control AI[/bold #06B6D4]\n\n"
        "Satélite de telecomunicações em órbita baixa (LEO), estilo Starlink/OneWeb.\n"
        "Monitora latência de uplink, throughput do feixe, saúde da antena\n"
        "phased-array, beam steering e carga térmica do transponder.\n\n"
        "[bold]Impacto terrestre:[/bold] internet para escolas rurais, telemedicina\n"
        "e pequenos negócios sem fibra. Cada alerta é traduzido no que significa\n"
        "para a comunidade conectada lá embaixo.\n\n"
        "[#8484A0]Global Solution 2026.1 · Prompt Engineering and AI · FIAP[/#8484A0]",
        title=" ◆ Sobre", border_style="#A855F7"))


def run_cli(engine):
    """Loop principal da CLI."""
    show_banner()
    if not engine.is_ready():
        console.print(" ⚠ Engine status: AGUARDANDO IMPLEMENTAÇÃO ✗ \n",
                      style="yellow")
    else:
        console.print(" ✓ Engine status: OPERACIONAL", style="green")
        if getattr(engine, "api_key_ok", True):
            console.print(" ✓ API KEY Ollama: carregada\n", style="green")
        else:
            console.print(" ⚠ API KEY Ollama: FALTANDO — defina OLLAMA_API_KEY "
                          "no arquivo .env\n", style="yellow")

    while True:
        try:
            user_input = session.prompt(" ❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not user_input:
            continue
        if user_input == "/exit":
            console.print("Encerrando Mission Control. Até a próxima órbita. 🛰",
                          style="#06B6D4")
            break
        if user_input == "/help":
            show_help()
            continue
        if user_input == "/about":
            show_about()
            continue
        if user_input == "/status":
            show_response(engine.status_snapshot())
            continue
        if user_input == "/impact":
            # Modo narrativa: dá palco para o impacto terrestre de cada alerta
            show_response(engine.impact_report())
            continue
        if user_input == "/clear":
            console.clear()
            show_banner()
            continue
        # Qualquer outra entrada vai para o motor de análise
        resposta = engine.analyze(user_input)
        show_response(resposta)
