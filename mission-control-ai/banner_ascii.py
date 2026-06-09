"""Script auxiliar standalone — gera o banner ASCII do projeto.

Uso:
    python banner_ascii.py                 # Banner padrão
    python banner_ascii.py --fonts         # Lista as 570+ fontes do PyFiglet
    python banner_ascii.py --font slant --text "Mission Control AI"
    python banner_ascii.py --demo          # Demonstra 8 fontes lado a lado
"""
import sys
import pyfiglet
from rich.console import Console
from rich.align import Align
from rich.text import Text

console = Console()


def banner_padrao():
    """Gera as duas linhas do banner em ASCII art."""
    linha1 = pyfiglet.figlet_format("Global Solution", font="ansi_shadow")
    linha2 = pyfiglet.figlet_format("Mission Control AI", font="ansi_shadow")
    console.print(Align.center(Text(linha1, style="bold #A855F7")))
    console.print(Align.center(Text(linha2, style="bold #06B6D4")))
    console.print(Align.center(
        Text(" ── 2026.1 · Prompt Engineering and AI · FIAP ── ",
             style="italic #8484A0")
    ))


def listar_fontes():
    fontes = pyfiglet.FigletFont.getFonts()
    console.print(f"[bold]{len(fontes)} fontes disponíveis no PyFiglet:[/bold]\n")
    for f in sorted(fontes):
        console.print(f, end="  ")
    console.print()


def testar_fonte(font, text):
    try:
        arte = pyfiglet.figlet_format(text, font=font)
        console.print(Text(arte, style="bold #06B6D4"))
    except pyfiglet.FontNotFound:
        console.print(f"[red]Fonte '{font}' não encontrada.[/red]")


def demo():
    fontes = ["ansi_shadow", "slant", "standard", "big",
              "banner3", "doom", "small", "block"]
    for f in fontes:
        console.print(f"[#8484A0]── {f} ──[/#8484A0]")
        try:
            console.print(Text(pyfiglet.figlet_format("Mission Control AI", font=f),
                               style="bold #06B6D4"))
        except pyfiglet.FontNotFound:
            console.print(f"[red](fonte {f} indisponível)[/red]")


def main():
    args = sys.argv[1:]
    if not args:
        banner_padrao()
        return
    if "--fonts" in args:
        listar_fontes()
        return
    if "--demo" in args:
        demo()
        return
    if "--font" in args:
        font = args[args.index("--font") + 1]
        text = "Mission Control AI"
        if "--text" in args:
            text = args[args.index("--text") + 1]
        testar_fonte(font, text)
        return
    banner_padrao()


if __name__ == "__main__":
    main()
