# powerup.py
"""
Power-ups recolectables — piedras preciosas / huevos de dinosaurio.

Al recoger un power-up, game.py envuelve al Player con el decorador
correspondiente (patrón Decorator):
  fire    → FireDecorator    (🔥 velocidad)
  ice     → IceDecorator     (❄️  escudo)
  thunder → ThunderDecorator (⚡ invencibilidad)
  nature  → NatureDecorator  (🌿 regeneración)
"""

import pygame
import math
import random
from setting import (
    POWERUP_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK,
    AURA_FIRE, AURA_ICE, AURA_THUNDER, AURA_HEAL,
)


class PowerUp(pygame.sprite.Sprite):
    """
    Gema prehistórica flotante.
    Cada tipo tiene un color, símbolo y efecto asociado.
    """

    TYPES = {
        "fire":    {"color": AURA_FIRE,    "symbol": "🔥", "label": "Fuego",  "ascii": "F"},
        "ice":     {"color": AURA_ICE,     "symbol": "❄️",  "label": "Hielo",  "ascii": "H"},
        "thunder": {"color": AURA_THUNDER, "symbol": "⚡", "label": "Rayo",   "ascii": "R"},
        "nature":  {"color": AURA_HEAL,    "symbol": "🌿", "label": "Natura", "ascii": "N"},
    }

    def __init__(self, kind: str = None):
        super().__init__()
        self.kind  = kind or random.choice(list(self.TYPES.keys()))
        self.info  = self.TYPES[self.kind]
        self.timer = 0
        self.size  = POWERUP_SIZE

        # Posición aleatoria alejada de los bordes
        self.base_x = random.randint(60, SCREEN_WIDTH - 60)
        self.base_y = random.randint(80, SCREEN_HEIGHT - 80)

        self.image = self._make_image()
        self.rect  = self.image.get_rect(center=(self.base_x, self.base_y))

    def _make_image(self) -> pygame.Surface:
        """Crea la imagen de la gema/huevo prehistórico."""
        total = self.size + 8
        surf = pygame.Surface((total, total), pygame.SRCALPHA)
        cx, cy = total // 2, total // 2
        r  = self.size // 2
        color = self.info["color"]

        # Forma de gema — diamante con brillo
        points = [
            (cx, cy - r),          # arriba
            (cx + r, cy),          # derecha
            (cx, cy + r),          # abajo
            (cx - r, cy),          # izquierda
        ]
        # Gema sólida
        pygame.draw.polygon(surf, (*color, 220), points)
        # Borde brillante
        pygame.draw.polygon(surf, (255, 255, 255, 100), points, 2)
        # Reflejo interno (triangulito claro arriba-izquierda)
        highlight = [
            (cx, cy - r + 3),
            (cx - r + 5, cy),
            (cx, cy - 2),
        ]
        pygame.draw.polygon(surf, (255, 255, 255, 60), highlight)

        # Letra identificadora
        try:
            font = pygame.font.SysFont(None, 18)
            txt  = font.render(self.info["ascii"], True, BLACK)
            surf.blit(txt, (cx - txt.get_width() // 2,
                            cy - txt.get_height() // 2))
        except Exception:
            pass

        return surf

    def update(self):
        self.timer += 1

        # Flotación senoidal
        offset_y = int(math.sin(self.timer * 0.07) * 6)
        # Balanceo horizontal sutil
        offset_x = int(math.sin(self.timer * 0.04) * 2)

        # Regenerar imagen con halo pulsante
        base_img = self._make_image()
        pulse = abs(math.sin(self.timer * 0.1))

        # Halo de resplandor
        halo_r = int(self.size // 2 + 6 + pulse * 5)
        halo_size = halo_r * 2 + 4
        final = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)

        # Halo exterior
        color = self.info["color"]
        alpha = int(40 + pulse * 70)
        pygame.draw.circle(final, (*color, alpha),
                           (halo_size // 2, halo_size // 2), halo_r)
        # Halo interior más intenso
        pygame.draw.circle(final, (*color, alpha + 30),
                           (halo_size // 2, halo_size // 2), halo_r - 3, 2)

        # Centrar la gema dentro del halo
        gx = halo_size // 2 - base_img.get_width() // 2
        gy = halo_size // 2 - base_img.get_height() // 2
        final.blit(base_img, (gx, gy))

        self.image = final
        self.rect  = self.image.get_rect(
            center=(self.base_x + offset_x, self.base_y + offset_y)
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)