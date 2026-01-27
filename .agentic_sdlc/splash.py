#!/usr/bin/env python3
"""
Splash Screen - SDLC Agêntico
Arte ASCII com mice à esquerda e dolphins à direita
"""

import sys
import time
import re
from pathlib import Path

# Função para ler versão do arquivo VERSION
def get_version():
    """Lê a versão do arquivo .claude/VERSION"""
    try:
        # Detecta o diretório do projeto
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent  # .agentic_sdlc -> root
        version_file = project_root / '.claude' / 'VERSION'

        if version_file.exists():
            content = version_file.read_text(encoding='utf-8')
            # Extrai versão usando regex: version: "X.Y.Z"
            match = re.search(r'version:\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except Exception:
        pass

    # Fallback se não conseguir ler
    return "not found"

# Cores ANSI
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ASCII Art - Trocado corretamente: MICE à esquerda, DOLPHINS à direita
# Original tinha dolphins à esquerda e mice à direita - agora invertido
LOGO_ASCII = r'''
.
                _                       __                                                __
              /   \                  /      \                                        _.-~  )
              '      \              /          \                          _..--~~~~,'   ,-/     _
            |       |Oo          o|            |                       .-'. . . .'   ,-','    ,' )
            `    \  |OOOo......oOO|   /        |                     ,'. . . _   ,--~,-'__..-'  ,'
             `    \\OOOOOOOOOOOOOOO\//        /                    ,'. . .  (@)' ---~~~~      ,'
               \ _o\OOOOOOOOOOOOOOOO//. ___ /                     /. . . . '~~             ,-'
            --- OO'* `OOOOOOOOOO'*  `OOOOO--                     /. . . . .             ,-'
                `OOOooOOOOOOOOOooooOOOOOO'OOOo                  ; . . . .  - .        ,'
              .OO "OOOOOOOOOOOOOOOOOOOO"OOOOOOOo               : . . . .       _     /
           OOOOO^OOOO0`(mice)/"OOOOOOOOOOOOO^OOOOOO           . . . . .          `-.:
           `OOOOO 0000000000000000 QQQQ "OOOOOOO"            . . . ./  - .          )
             "OOOOOOO00000000000000000OOOOOOOOOO"           .  . . |  _____..---.._/ _____
  .ooooOOOOOOOo"OOOOOOO000000000000OOOOOOOOOOO"       ~---~~~~----~~~~             ~~
.OOO"""""""""".oOOOOOOOOOOOOOOOOOOOOOOOOOOOOo      
  `"OOOOOOOOOOOOoooooooo.                          
'''

COL_SEPARA = 51

TITLE = r"""
   ____  ___  _     ___      _                 _   _
  / ___||   \| |   / __|    /_\  __ _ ___ _ _ | |_(_)__ ___
  \___ \| |) | |__ | (__   / _ \/ _` / -_) ' \|  _| / _/ _ \
  |____/|___/|____| \___| /_/ \_\__, \___|_||_|\__|_\__\___/
                                |___/
"""

def clear_screen():
    """Limpa a tela do terminal."""
    print("\033[2J\033[H", end="")
    sys.stdout.flush()

def print_colored_logo():
    """Imprime o logo com cores - mice em branco (esquerda), dolphins em ciano (direita)."""
    lines = LOGO_ASCII.strip().split('\n')

    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            # Dividir a linha - mice à esquerda (branco), dolphins à direita (ciano)
            # Split point é aproximadamente coluna 51
            if len(line) > COL_SEPARA:
                left = line[:COL_SEPARA]
                right = line[COL_SEPARA:]
                print(f"{WHITE}{left}{RESET}{CYAN}{right}{RESET}")
            else:
                print(f"{WHITE}{line}{RESET}")
        else:
            # Última linha com os labels
            print(f"{BOLD}{line}{RESET}")

def print_title():
    """Imprime o título estilizado."""
    if TITLE:
        print(f"{BOLD}{CYAN}{TITLE}{RESET}")

def print_info():
    """Imprime informações do projeto."""
    version = get_version()

    print(f"\n{DIM}{'─' * 80}{RESET}")
    print(f"\n{WHITE}  🚀 {BOLD}Framework de Orquestração de Desenvolvimento{RESET}")
    print(f"{WHITE}     {BOLD}Orientado por Agentes de IA{RESET}")
    print(f"{DIM}     Cobrindo todas as fases do ciclo de vida de software{RESET}")
    print(f"\n{GREEN}  ▸ {WHITE}Repositório: {CYAN}github.com/arbgjr/sdlc_agentico{RESET}")
    print(f"{GREEN}  ▸ {WHITE}Versão:      {YELLOW}{version}{RESET}")
    print(f"{GREEN}  ▸ {WHITE}Licença:     {MAGENTA}MIT{RESET}")
    print(f"{GREEN}  ▸ {WHITE}Changelog:   {CYAN}github.com/arbgjr/sdlc_agentico/blob/main/CHANGELOG.md{RESET}")

    # Changelog resumido da versão atual
    print(f"\n{DIM}{'─' * 80}{RESET}")
    print(f"\n{YELLOW}  📋 {BOLD}v{version} Highlights{RESET}")
    print(f"{DIM}     Configuration & Path Management - Critical Fixes{RESET}")
    print(f"{GREEN}     • {WHITE}Configurable Output Directories - settings.json support for project/framework paths{RESET}")
    print(f"{GREEN}     • {WHITE}Fixed project_path Bug - Auto-detect skill directory vs CWD{RESET}")
    print(f"{GREEN}     • {WHITE}Removed ALL Hardcoded Paths - Dynamic path construction everywhere{RESET}")
    print(f"{GREEN}     • {WHITE}Settings Priority - settings.json > import_config.yml > default{RESET}")
    print(f"{GREEN}     • {WHITE}Framework/Project Separation - Clear REGRA DE OURO documentation{RESET}")

    print(f"\n{DIM}{'─' * 80}{RESET}")
    print(f"\n{DIM}  Comandos principais:{RESET}")
    print(f"  {CYAN}/sdlc-start{WHITE}         Inicia novo workflow SDLC completo{RESET}")
    print(f"  {CYAN}/sdlc-import{WHITE}        Importa projeto existente (até 900k LOC){RESET}")
    print(f"  {CYAN}/wiki-sync{WHITE}          Sincroniza docs com GitHub Wiki {DIM}(criar 1ª página antes){RESET}")
    print()

def animate_splash():
    """Exibe a splash screen com animação."""
    clear_screen()
    print_colored_logo()
    time.sleep(0.3)
    print_title()
    time.sleep(0.2)
    print_info()

def show_splash(animate: bool = True):
    """Exibe a splash screen."""
    if animate:
        animate_splash()
    else:
        # No-animate mode: don't clear screen to preserve context
        print_colored_logo()
        print_title()
        print_info()

if __name__ == "__main__":
    no_animate = "--no-animate" in sys.argv or "-n" in sys.argv
    show_splash(animate=not no_animate)
