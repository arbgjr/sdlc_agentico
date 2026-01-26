#!/usr/bin/env python3
"""
Splash Screen - SDLC Agêntico
Arte ASCII gerada a partir do logo do projeto
"""

import sys
import time

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

LOGO_ASCII = r'''
                                       __
                                  _.-~  )
                       _..--~~~~,'   ,-/     _
                    .-'. . . .'   ,-','    ,' )
                  ,'. . . _   ,--~,-'__..-'  ,'
                ,'. . .  (@)' ---~~~~      ,'
               /. . . . '~~             ,-'
              /. . . . .             ,-'
             ; . . . .  - .        ,'
            : . . . .       _     /
           . . . . .          `-.:
          . . . ./  - .          )
         .  . . |  _____..---.._/ _____
   ~---~~~~----~~~~             ~~
'''

MOUSE_ASCII = r'''
                _                       __
              /   \                  /      \
             '      \              /          \
            |       |Oo          o|            |
            `    \  |OOOo......oOO|   /        |
             `    \\OOOOOOOOOOOOOOO\//        /
               \ _o\OOOOOOOOOOOOOOOO//. ___ /
            --- OO'* `OOOOOOOOOO'*  `OOOOO--
                `OOOooOOOOOOOOOooooOOOOOO'OOOo
              .OO "OOOOOOOOOOOOOOOOOOOO"OOOOOOOo
           OOOOO^OOOO0`(mice)/"OOOOOOOOOOOOO^OOOOOO
           `OOOOO 0000000000000000 QQQQ "OOOOOOO"
             "OOOOOOO00000000000000000OOOOOOOOOO"
  .ooooOOOOOOOo"OOOOOOO000000000000OOOOOOOOOOO"
.OOO"""""""""".oOOOOOOOOOOOOOOOOOOOOOOOOOOOOo
  `"OOOOOOOOOOOOoooooooo.
'''

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

def print_colored_logo():
    """Imprime o logo com cores - golfinho em ciano, camundongo em branco."""
    # Golfinho em ciano
    for line in LOGO_ASCII.strip().split('\n'):
        print(f"{CYAN}{line}{RESET}")
    
    # Camundongo em branco
    for line in MOUSE_ASCII.strip().split('\n'):
        print(f"{WHITE}{line}{RESET}")

def print_title():
    """Imprime o título estilizado."""
    if TITLE:
        print(f"{BOLD}{CYAN}{TITLE}{RESET}")

def print_info():
    """Imprime informações do projeto."""
    print(f"\n{DIM}{'─' * 68}{RESET}")
    print(f"\n{WHITE}  🚀 {BOLD}Framework de Orquestração de Desenvolvimento{RESET}")
    print(f"{WHITE}     {BOLD}Orientado por Agentes de IA{RESET}")
    print(f"{DIM}     Cobrindo todas as fases do ciclo de vida de software{RESET}")
    print(f"\n{GREEN}  ▸ {WHITE}Repositório: {CYAN}github.com/arbgjr/sdlc_agentico{RESET}")
    print(f"{GREEN}  ▸ {WHITE}Versão:      {YELLOW}1.0.0{RESET}")
    print(f"{GREEN}  ▸ {WHITE}Licença:     {MAGENTA}MIT{RESET}")
    print(f"\n{DIM}{'─' * 68}{RESET}")
    print(f"\n{DIM}  Comandos principais:{RESET}")
    print(f"  {CYAN}/sdlc-start{WHITE}         Inicia novo workflow{RESET}")
    print(f"  {CYAN}/sdlc-create-issues{WHITE} Cria issues no GitHub{RESET}")
    print(f"  {CYAN}/gate-check{WHITE}         Valida transição de fase{RESET}")
    print(f"  {CYAN}/adr-create{WHITE}         Registra decisão arquitetural{RESET}")
    print()

def animate_splash(delay: float = 0.02):
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
        clear_screen()
        print_colored_logo()
        print_title()
        print_info()

if __name__ == "__main__":
    no_animate = "--no-animate" in sys.argv or "-n" in sys.argv
    show_splash(animate=not no_animate)
