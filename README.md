# Asteroids Pygame v1

Jogo estilo Asteroids feito em Python com Pygame, com foco em arquitetura simples, mecânicas clássicas e evolução de dificuldade por ondas.

## Visão geral

Este projeto implementa um jogo singleplayer com:

- Nave com movimento inercial (rotação, acelacao e atrito)
- Asteroides com fragmentacao por tamanho (L -> M -> S)
- Sistema de pontuacao por destruicao de inimigos
- UFOs com tiros e nivel de mira diferente por tipo
- Hiperespaco com custo de pontuacao
- Sistema de vidas e game over
- Power-ups de escudo e vida extra
- HUD com score, vidas e wave

## Requisitos

- Python 3.10+ (recomendado 3.12)
- Pygame (ja listado em requirements.txt)

## Instalacao

No Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como executar

Com ambiente virtual ativo:

```bash
python src/main.py
```

Sem ativar ambiente (Windows):

```powershell
.\.venv\Scripts\python.exe src/main.py
```

## Controles

- Seta esquerda: gira para a esquerda
- Seta direita: gira para a direita
- Seta para cima: acelera
- Espaco: atira
- Shift esquerdo: hiperespaco (consome pontos)
- Enter ou Espaco na tela de game over: reinicia a partida
- ESC:
  - durante o jogo/menu: fecha o jogo
  - na tela de game over: volta ao menu principal

## Mecânicas

### Ondas e progressao

- A cada nova wave aumenta a quantidade de asteroides
- Nova wave inicia quando todos os asteroides forem destruidos

### Asteroides

- Tamanho L: menor pontuacao, divide em dois M
- Tamanho M: pontuacao media, divide em dois S
- Tamanho S: maior pontuacao, nao divide

### UFOs

- Spawn periodico
- UFO grande: menor precisao
- UFO pequeno: maior precisao e maior recompensa

### Power-ups

- Podem cair ao destruir asteroides
- Tipos:
  - `shield`: ativa escudo temporario na nave
  - `life`: concede vida extra

## Estrutura do projeto

```text
src/
  config.py    # Constantes de gameplay e balanceamento
  game.py      # Loop principal, cenas e renderizacao de UI
  main.py      # Ponto de entrada
  sprites.py   # Entidades (nave, asteroide, tiros, UFO, power-up)
  systems.py   # Estado do mundo, colisao, pontuacao e progressao
  utils.py     # Utilitarios matematicos e funcoes de desenho
```

## Configuracao

Os principais ajustes de balanceamento ficam em `src/config.py`, incluindo:

- resolucao, FPS e cores
- velocidade da nave e taxa de tiro
- velocidade e tamanho dos asteroides
- spawn e comportamento dos UFOs
- duracao/chance de power-ups

## Desenvolvimento

Para instalar dependencias em ambiente limpo:

```bash
pip install -r requirements.txt
```

Para congelar novas dependencias:

```bash
pip freeze > requirements.txt
```

## Licenca

Este projeto utiliza a licenca MIT. Consulte o arquivo LICENSE para detalhes.
