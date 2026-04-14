# ASTEROIDE SINGLEPLAYER v1.0
# This file stores the gameplay, rendering, and balancing constants.

WIDTH = 960
HEIGHT = 720
FPS = 60

START_LIVES = 3
SAFE_SPAWN_TIME = 2.0
WAVE_DELAY = 2.0

SHIP_RADIUS = 15
SHIP_TURN_SPEED = 220.0
SHIP_THRUST = 220.0
SHIP_FRICTION = 0.995
SHIP_FIRE_RATE = 0.2
SHIP_BULLET_SPEED = 420.0
HYPERSPACE_COST = 250

AST_VEL_MIN = 30.0
AST_VEL_MAX = 90.0
AST_SIZES = {
    "L": {"r": 46, "score": 20, "split": ["M", "M"]},
    "M": {"r": 24, "score": 50, "split": ["S", "S"]},
    "S": {"r": 12, "score": 100, "split": []},
}

BULLET_RADIUS = 2
BULLET_TTL = 1.0
MAX_BULLETS = 4

UFO_SPAWN_EVERY = 15.0
UFO_SPEED = 80.0
UFO_FIRE_EVERY = 1.2
UFO_BULLET_SPEED = 260.0
UFO_BULLET_TTL = 1.8
UFO_BIG = {"r": 18, "score": 200, "aim": 0.2}
UFO_SMALL = {"r": 12, "score": 1000, "aim": 0.6}

WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)

RANDOM_SEED = None

# Duração do fade-in da tela de game over (segundos)
GAME_OVER_FADE_DURATION = 1.5

# POWER-UPS E ESCUDOS
POWERUP_RADIUS = 12
POWERUP_TTL = 10.0           # Tempo que o power-up fica na tela antes de sumir
SHIELD_DURATION = 8.0        # Tempo de duração do escudo na nave
POWERUP_DROP_CHANCE = 0.15   # 15% de chance de dropar ao destruir um asteroide
# TIRO DUPLO
DOUBLE_SHOT_DURATION = 10.0  # Duração do tiro duplo em segundos
DOUBLE_SHOT_SPREAD = 10.0    # Ângulo de abertura entre os dois tiros (graus)

# LASER
LASER_DURATION = 8.0         # Duração do power-up de laser (segundos de uso)
LASER_CHARGE_MAX = 3         # Número de disparos de laser por power-up
LASER_WIDTH = 3              # Largura visual do feixe de laser
LASER_TTL = 0.12             # Duração do raio laser na tela (segundos)
LASER_COLOR = (80, 220, 255) # Cor do laser (azul-ciano)
LASER_SCORE_MULT = 1         # Multiplicador de score ao destruir com laser

# COMBO
COMBO_WINDOW = 5.0
COMBO_MAX = 4

# BOSS
BOSS_WAVE_INTERVAL = 5
BOSS_RADIUS = 60
BOSS_HP = 300
BOSS_SCORE = 2000
BOSS_CONTACT_DAMAGE_COOLDOWN = 1.0

BOSS_SPEED_PHASE1 = 55.0
BOSS_SPEED_PHASE2 = 85.0
BOSS_SPEED_PHASE3 = 120.0

BOSS_FIRE_COOLDOWN_PHASE1 = 2.0
BOSS_FIRE_COOLDOWN_PHASE2 = 1.2
BOSS_FIRE_COOLDOWN_PHASE3 = 0.7

BOSS_BULLET_SPEED = 220.0
BOSS_BULLET_TTL = 3.0
BOSS_BULLET_RADIUS = 3

BOSS_PHASE2_SUMMON_COOLDOWN = 3.5

# Probabilidade de drop de cada tipo de power-up (somam 1.0)
# shield=0.40, life=0.20, double_shot=0.25, laser=0.15
POWERUP_WEIGHTS = {
    "shield": 0.40,
    "life": 0.20,
    "double_shot": 0.25,
    "laser": 0.15,
}
