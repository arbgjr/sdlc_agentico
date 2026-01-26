# Splash Screen Integration - SDLC Agêntico

## O que é?

**`splash.py`** é uma splash screen ASCII art que exibe:
- Logo do projeto (Dolphins 🐬 e Mice 🐭)
- Título estilizado do SDLC Agêntico
- Informações do projeto (repositório, versão, licença)
- Comandos principais para começar

## Onde é usado?

### 1. Durante Instalação (setup-sdlc.sh)

Após a instalação completa, o `splash.py` é automaticamente exibido antes do resumo final:

```bash
./\.agentic_sdlc/scripts/setup-sdlc.sh
# ...instalação...
# [Splash screen aparece aqui]
# Próximos passos...
```

**Implementação:**
```bash
# Em setup-sdlc.sh, função print_summary()
if [[ -f ".agentic_sdlc/splash.py" ]]; then
    python3 .agentic_sdlc/splash.py --no-animate 2>/dev/null || true
    sleep 1
fi
```

### 2. Manual (quando quiser)

```bash
# Com animação
python3 .agentic_sdlc/splash.py

# Sem animação (mais rápido)
python3 .agentic_sdlc/splash.py --no-animate
```

## Características

- **Cores:** Golfinho em ciano, camundongo em branco
- **Animação opcional:** Use `--no-animate` para pular animação
- **Fail-safe:** Se falhar, instalação continua normalmente
- **Zero dependências:** Usa apenas stdlib do Python

## Customização

A versão é lida automaticamente de `.claude/VERSION`:

```python
def get_version():
    """Lê a versão do arquivo .claude/VERSION"""
    # Busca version: "X.Y.Z" no arquivo
    # Retorna "not found" se não encontrar
```

Para atualizar a versão exibida, edite `.claude/VERSION`:

```yaml
version: "2.1.2"  # ← Atualizar aqui
```

## Quando NÃO é exibida

- Se `.agentic_sdlc/splash.py` não existe
- Se Python 3 não está disponível
- Se terminal não suporta cores ANSI (fallback gracioso)

## Benefícios

✅ **Onboarding visual** - Novo usuário recebe feedback visual de sucesso
✅ **Branding** - Reforça identidade do projeto (Dolphins + Mice)
✅ **Guia rápido** - Mostra comandos principais logo após instalação
✅ **Profissionalismo** - Adiciona polish à experiência do usuário

## Futuras Integrações

Potenciais lugares para usar o splash:

1. ✅ **Setup script** (implementado)
2. **CLI de versão:** `claude --version` poderia mostrar splash
3. **Comando dedicado:** `/splash` ou `/about` para mostrar informações
4. **Hook de onboarding:** Primeira vez que usuário roda um comando SDLC
5. **GitHub README:** Screenshot da splash no README principal

## Manutenção

**Quando atualizar:**
- Sempre que a versão do framework mudar (em `splash.py` linha 82)
- Se novos comandos principais forem adicionados (linhas 86-89)
- Se houver mudança de branding ou logo

**Como testar:**
```bash
# Teste rápido
python3 .agentic_sdlc/splash.py --no-animate

# Teste integrado no setup
./\.agentic_sdlc/scripts/setup-sdlc.sh --skip-deps
```
