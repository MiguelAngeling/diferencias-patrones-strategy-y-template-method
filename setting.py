# setting.py
"""
Configuración centralizada del juego Dinosaurio con Patrón Decorador.
Todas las constantes del juego se definen aquí para fácil ajuste.
"""

# ── Pantalla ──────────────────────────────────────────────────
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
TITLE         = "Dino Aura — Strategy + Template Method + Decorator"
FPS           = 60

# ── Colores base ──────────────────────────────────────────────
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GREY   = (128, 128, 128)

# Colores del entorno
BG_TOP      = (15, 12, 30)
BG_BOTTOM   = (35, 55, 45)
STAR_COLOR  = (60, 60, 100)

# Jugador y enemigos
PLAYER_COLOR = (30, 70, 34)
ENEMY_COLOR  = (200, 60, 60)

# ── Aura de decoradores ──────────────────────────────────────
AURA_FIRE    = (255, 100, 20)
AURA_ICE     = (100, 220, 255)
AURA_THUNDER = (255, 240, 40)
AURA_HEAL    = (60, 220, 80)

# ── Dinosaurio (sprites) ─────────────────────────────────────
DINO_SCALE       = (64, 64)
DINO_ANIM_SPEED  = 6
DINO_SPRITES_DIR = "src"

DINO_ANIMS = {
    "Idle": 10,
    "Run":   8,
    "Walk": 10,
    "Jump": 12,
    "Dead":  8,
}

# ── Físicas ──────────────────────────────────────────────────
PLAYER_SIZE   = 64
PLAYER_SPEED  = 4
ENEMY_SIZE    = 36
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 4

# ── Power-ups ────────────────────────────────────────────────
POWERUP_SIZE     = 28
POWERUP_DURATION = 420

# ── Juego ────────────────────────────────────────────────────
INITIAL_LIVES       = 3
MAX_LIVES           = 5
ENEMY_SPAWN_MIN     = 30
ENEMY_SPAWN_BASE    = 60
POWERUP_SPAWN_INTERVAL = 360

# ── Partículas ambientales ────────────────────────────────────
AMBIENT_PARTICLE_COUNT = 40
AMBIENT_PARTICLE_COLOR = (80, 120, 70, 60)
